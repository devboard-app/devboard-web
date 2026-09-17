from web.services.client import call
from web.services.exceptions import ServiceError


async def resolve_usernames(request, user_ids: list[str]) -> dict[str, str]:
    """Map user_id -> username for display, via devboard-core's batch lookup.

    Team/project membership rows only carry a user_id -- this is the one
    place that turns those into something readable. Best-effort: a resolve
    failure degrades to showing raw ids instead of breaking the page.
    """
    unique_ids = list(dict.fromkeys(user_ids))
    if not unique_ids:
        return {}
    try:
        response = await call(request, 'POST', 'core', '/api/users/batch/', json={'ids': unique_ids})
    except ServiceError:
        return {}
    return {user['user_id']: user['username'] for user in response.json()}
