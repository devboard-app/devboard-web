from web.services.client import call
from web.services.exceptions import ServiceError

UNREAD_SAMPLE_LIMIT = 100


async def get_unread_count(request) -> int:
    """Best-effort sidebar badge count. devboard-integrations has no dedicated
    unread-count endpoint, so this samples the most recent UNREAD_SAMPLE_LIMIT
    notifications (already sorted newest-first) and counts the unread ones --
    exact up to that many, undercounts beyond it. A ServiceError just means no
    badge shows, not a broken page."""
    try:
        response = await call(request, 'GET', 'integrations', '/api/notifications/', params={'limit': UNREAD_SAMPLE_LIMIT})
    except ServiceError:
        return 0
    return sum(1 for n in response.json()['results'] if not n['read'])
