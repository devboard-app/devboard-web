from datetime import datetime, timedelta, timezone

from web.services.client import call
from web.services.exceptions import ServiceError


async def login(request, email: str, password: str) -> None:
    response = await call(request, 'POST', 'auth', '/auth/login/', json={'email': email, 'password': password})
    data = response.json()

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=data['expires_in'])
    request.session['access_token'] = data['access_token']
    request.session['refresh_token'] = data['refresh_token']
    request.session['access_token_expires_at'] = expires_at.isoformat()
    request.session['email'] = email

    me = await call(request, 'GET', 'core', '/api/users/me/')
    request.session['user_id'] = me.json()['user_id']

async def logout(request) -> None:
    refresh_token = request.session.get('refresh_token')
    if refresh_token:
        try:
            await call(request, 'POST', 'auth', '/auth/logout/', json={'refresh_token': refresh_token})
        except ServiceError:
            pass # user should still get logged out locally even if this fails
    request.session.flush()

async def register(request, email: str, password: str) -> None:
    await call(request, 'POST', 'auth', '/auth/register/', json={'email': email, 'password': password})

async def verify_email(request, token: str) -> None:
    await call(request, 'GET', 'auth', '/auth/verify-email/', params={'token': token})

async def resend_verification(request, email: str) -> None:
    await call(request, 'POST', 'auth', '/auth/resend-verification/', json={'email': email})

async def forgot_password(request, email: str) -> None:
    await call(request, 'POST', 'auth', '/auth/forgot-password/', json={'email': email})

async def reset_password(request, token: str, password: str) -> None:
    await call(request, 'POST', 'auth', '/auth/reset-password/', json={'token': token, 'password': password})