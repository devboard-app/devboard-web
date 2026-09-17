from web.services.client import call
from web.services.exceptions import ServiceError


async def get_my_team_role(request, team_id) -> str | None:
    """Best-effort: unreachable work service just means no manager actions show."""
    try:
        response = await call(request, 'GET', 'work', f'/api/teams/{team_id}/members/', params={'limit': 100})
    except ServiceError:
        return None
    my_user_id = request.session.get('user_id')
    membership = next((m for m in response.json()['results'] if m['user_id'] == my_user_id), None)
    return membership['role'] if membership else None
