from datetime import datetime, timedelta, timezone

import httpx
import redis.asyncio as aioredis
from django.conf import settings

from web.services.exceptions import ServiceError

REFRESH_SKEW_SECONDS = 15
TIMEOUT = 3.0
SERVICE_URLS = {
    "auth": settings.AUTH_SERVICE_URL,
    "core": settings.CORE_SERVICE_URL,
    "work": settings.WORK_SERVICE_URL,
    "analytics": settings.ANALYTICS_SERVICE_URL,
    "attachments": settings.ATTACHMENTS_SERVICE_URL,
    "integrations": settings.INTEGRATIONS_SERVICE_URL,
}



def raise_for_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return

    try:
        body = response.json()
        detail = body.get("detail", "Unexpected error.")
        errors = body.get("errors")
    except ValueError:
        detail = "Unexpected error."
        errors = None

    raise ServiceError(detail=detail, errors=errors, status_code=response.status_code)


def needs_refresh(request) -> bool:
    expires_at_raw = request.session.get('access_token_expires_at')
    if not expires_at_raw:
        return False
    expires_at = datetime.fromisoformat(expires_at_raw)
    return datetime.now(timezone.utc) >= expires_at - timedelta(seconds=REFRESH_SKEW_SECONDS)


def _lock_key(request) -> str:
    return getattr(request.session, 'session_key', None) or request.session.get('refresh_token', 'anonymous')


async def _perform_refresh(request) -> None:
    refresh_token = request.session.get('refresh_token')
    async with httpx.AsyncClient(base_url=SERVICE_URLS['auth'], timeout=TIMEOUT) as http:
        response = await http.post('/auth/refresh-token/', json={'refresh_token': refresh_token})

    raise_for_status(response)
    data = response.json()

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=data['expires_in'])
    request.session['access_token'] = data['access_token']
    request.session['refresh_token'] = data['refresh_token']
    request.session['access_token_expires_at'] = expires_at.isoformat()


async def _refresh_access_token(request) -> None:
    if not needs_refresh(request):
        return
    
    async with (aioredis.from_url(settings.REDIS_URL) as redis_client,
         redis_client.lock(f"refresh-lock:{_lock_key(request)}", timeout=5, blocking_timeout=5)):
            if needs_refresh(request):
                await _perform_refresh(request)


async def _force_refresh(request, failed_token: str) -> None:
    async with (aioredis.from_url(settings.REDIS_URL) as redis_client,
        redis_client.lock(f"refresh-lock:{_lock_key(request)}", timeout=5, blocking_timeout=5)):
            if request.session.get('access_token') == failed_token:
                await _perform_refresh(request)


async def _do_request(request, method: str, service: str, path: str, **kwargs) -> httpx.Response:
    base_url = SERVICE_URLS[service]
    headers = kwargs.pop('headers', {})

    access_token = request.session.get('access_token')
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'

    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=TIMEOUT) as http:
            response = await http.request(method, path, headers=headers, **kwargs)
    except httpx.TransportError as exc:
        raise ServiceError(detail=f"{service} service is unavailable.") from exc

    raise_for_status(response)
    return response


async def call(request, method: str, service: str, path: str, **kwargs) -> httpx.Response:
    await _refresh_access_token(request)
    used_token = request.session.get('access_token')

    try:
        return await _do_request(request, method, service, path, **kwargs)
    except ServiceError as exc:
        if exc.status_code != 401 or not used_token:
            raise
        await _force_refresh(request, used_token)
        return await _do_request(request, method, service, path, **kwargs)