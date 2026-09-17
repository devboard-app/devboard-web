import asyncio

from django.shortcuts import render

from web.services.client import call
from web.services.exceptions import ServiceError


async def project_detail_view(request, team_id, project_id):
    tickets_result, activity_result = await asyncio.gather(
        call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/{project_id}/tickets/'),
        call(request, 'GET', 'analytics', f'/reports/projects/{project_id}/activity/summary/'),
        return_exceptions=True,
    )

    if isinstance(tickets_result, ServiceError):
        return render(request, 'error.html', {'detail': tickets_result.detail}, status=tickets_result.status_code)
    if isinstance(tickets_result, Exception):
        raise tickets_result

    activity = None if isinstance(activity_result, Exception) else activity_result.json()

    return render(request, 'projects/detail.html', {
        'tickets': tickets_result.json()['results'],
        'activity': activity,
    })
