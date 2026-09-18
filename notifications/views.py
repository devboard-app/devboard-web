from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from web.services.client import call
from web.services.exceptions import ServiceError
from web.services.pagination import page_context


async def notifications_list_view(request):
    limit = request.GET.get('limit', 20)
    offset = request.GET.get('offset', 0)

    try:
        response = await call(request, 'GET', 'integrations', '/api/notifications/', params={'limit': limit, 'offset': offset})
    except ServiceError as exc:
        return render(request, 'error.html', {'detail': exc.detail}, status=exc.status_code)

    context = page_context(response.json())
    context['unread'] = [n for n in context['results'] if not n['read']]
    context['earlier'] = [n for n in context['results'] if n['read']]
    return render(request, 'notifications/list.html', context)


@require_POST
async def notification_mark_read_view(request, notification_id):
    try:
        await call(request, 'PATCH', 'integrations', f'/api/notifications/{notification_id}/')
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect('/notifications/')


@require_POST
async def notification_mark_all_read_view(request):
    try:
        await call(request, 'PATCH', 'integrations', '/api/notifications/read-all/')
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect('/notifications/')


@require_POST
async def notification_delete_view(request, notification_id):
    try:
        await call(request, 'DELETE', 'integrations', f'/api/notifications/{notification_id}/')
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect('/notifications/')
