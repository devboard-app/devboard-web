import asyncio

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from web.services.client import call
from web.services.exceptions import ServiceError
from web.services.pagination import page_context
from web.services.teams import get_my_team_role, get_team_name
from web.services.users import resolve_usernames


async def project_list_view(request, team_id):
    limit = request.GET.get('limit', 20)
    offset = request.GET.get('offset', 0)

    try:
        response = await call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/', params={'limit': limit, 'offset': offset})
    except ServiceError as exc:
        return render(request, 'error.html', {'detail': exc.detail}, status=exc.status_code)

    my_team_role = await get_my_team_role(request, team_id)
    context = page_context(response.json())
    context['team_id'] = team_id
    context['team_name'] = await get_team_name(request, team_id)
    context['sidebar_active'] = 'projects'
    context['can_create'] = my_team_role in ('owner', 'admin')
    return render(request, 'projects/list.html', context)


async def project_create_view(request, team_id):
    team_name = await get_team_name(request, team_id)

    if request.method == 'POST':
        name = request.POST.get('name', '')
        key = request.POST.get('key', '').upper()
        description = request.POST.get('description', '')

        try:
            response = await call(request, 'POST', 'work', f'/api/teams/{team_id}/projects/', json={'name': name, 'key': key, 'description': description})
        except ServiceError as exc:
            context = {
                'error': exc.detail, 'errors': exc.errors, 'team_id': team_id, 'team_name': team_name,
                'sidebar_active': 'projects', 'name': name, 'key': key, 'description': description,
            }
            return render(request, 'projects/create.html', context)

        return redirect(f"/teams/{team_id}/projects/{response.json()['id']}/")

    return render(request, 'projects/create.html', {'team_id': team_id, 'team_name': team_name, 'sidebar_active': 'projects'})


async def project_detail_view(request, team_id, project_id):
    project_result, tickets_result, activity_result, members_result, team_name = await asyncio.gather(
        call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/{project_id}/'),
        call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/{project_id}/tickets/'),
        call(request, 'GET', 'analytics', f'/reports/projects/{project_id}/activity/summary/'),
        call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/{project_id}/members/', params={'limit': 100}),
        get_team_name(request, team_id),
        return_exceptions=True,
    )

    if isinstance(project_result, ServiceError):
        return render(request, 'error.html', {'detail': project_result.detail}, status=project_result.status_code)
    if isinstance(project_result, Exception):
        raise project_result
    if isinstance(tickets_result, ServiceError):
        return render(request, 'error.html', {'detail': tickets_result.detail}, status=tickets_result.status_code)
    if isinstance(tickets_result, Exception):
        raise tickets_result

    activity = None if isinstance(activity_result, Exception) else activity_result.json()

    is_lead = False
    if not isinstance(members_result, Exception):
        my_user_id = request.session.get('user_id')
        is_lead = any(m['user_id'] == my_user_id and m['role'] == 'lead' for m in members_result.json()['results'])

    return render(request, 'projects/detail.html', {
        'team_id': team_id,
        'team_name': team_name,
        'sidebar_active': 'overview',
        'project': project_result.json(),
        'tickets': tickets_result.json()['results'],
        'activity': activity,
        'is_lead': is_lead,
    })


async def project_edit_view(request, team_id, project_id):
    team_name = await get_team_name(request, team_id)

    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            try:
                await call(request, 'DELETE', 'work', f'/api/teams/{team_id}/projects/{project_id}/')
            except ServiceError as exc:
                messages.error(request, exc.detail)
                return redirect(f'/teams/{team_id}/projects/{project_id}/edit/')
            return redirect(f'/teams/{team_id}/projects/')

        name = request.POST.get('name', '')
        key = request.POST.get('key', '').upper()
        description = request.POST.get('description', '')

        try:
            await call(request, 'PATCH', 'work', f'/api/teams/{team_id}/projects/{project_id}/', json={'name': name, 'key': key, 'description': description})
        except ServiceError as exc:
            project = {'id': project_id, 'name': name, 'key': key, 'description': description}
            context = {
                'error': exc.detail, 'errors': exc.errors, 'team_id': team_id, 'team_name': team_name,
                'sidebar_active': 'overview', 'project': project,
            }
            return render(request, 'projects/edit.html', context)

        return redirect(f'/teams/{team_id}/projects/{project_id}/')

    try:
        response = await call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/{project_id}/')
    except ServiceError as exc:
        return render(request, 'error.html', {'detail': exc.detail}, status=exc.status_code)

    return render(request, 'projects/edit.html', {
        'team_id': team_id, 'team_name': team_name, 'sidebar_active': 'overview', 'project': response.json(),
    })


async def project_members_view(request, team_id, project_id):
    members_result, team_members_result, project_result, team_name = await asyncio.gather(
        call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/{project_id}/members/', params={'limit': 100}),
        call(request, 'GET', 'work', f'/api/teams/{team_id}/members/', params={'limit': 100}),
        call(request, 'GET', 'work', f'/api/teams/{team_id}/projects/{project_id}/'),
        get_team_name(request, team_id),
        return_exceptions=True,
    )

    if isinstance(members_result, ServiceError):
        return render(request, 'error.html', {'detail': members_result.detail}, status=members_result.status_code)
    if isinstance(members_result, Exception):
        raise members_result
    if isinstance(project_result, ServiceError):
        return render(request, 'error.html', {'detail': project_result.detail}, status=project_result.status_code)
    if isinstance(project_result, Exception):
        raise project_result

    members = members_result.json()['results']
    member_ids = {m['user_id'] for m in members}
    usernames = await resolve_usernames(request, [m['user_id'] for m in members])
    for member in members:
        member['username'] = usernames.get(member['user_id'], member['user_id'])

    my_user_id = request.session.get('user_id')
    is_lead = any(m['user_id'] == my_user_id and m['role'] == 'lead' for m in members)

    addable = []
    if not isinstance(team_members_result, Exception):
        team_members = [m for m in team_members_result.json()['results'] if m['user_id'] not in member_ids]
        team_usernames = await resolve_usernames(request, [m['user_id'] for m in team_members])
        addable = [{'user_id': m['user_id'], 'username': team_usernames.get(m['user_id'], m['user_id'])} for m in team_members]

    return render(request, 'projects/members.html', {
        'team_id': team_id,
        'team_name': team_name,
        'sidebar_active': 'members',
        'project': project_result.json(),
        'project_id': project_id,
        'members': members,
        'addable': addable,
        'is_lead': is_lead,
    })


@require_POST
async def project_member_add_view(request, team_id, project_id):
    user_id = request.POST.get('user_id', '')
    role = request.POST.get('role', '')

    try:
        await call(request, 'POST', 'work', f'/api/teams/{team_id}/projects/{project_id}/members/', json={'user_id': user_id, 'role': role})
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect(f'/teams/{team_id}/projects/{project_id}/members/')


@require_POST
async def project_member_remove_view(request, team_id, project_id, user_id):
    try:
        await call(request, 'DELETE', 'work', f'/api/teams/{team_id}/projects/{project_id}/members/{user_id}/')
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect(f'/teams/{team_id}/projects/{project_id}/members/')


@require_POST
async def project_member_role_view(request, team_id, project_id, user_id):
    role = request.POST.get('role', '')

    try:
        await call(request, 'PATCH', 'work', f'/api/teams/{team_id}/projects/{project_id}/members/{user_id}/', json={'role': role})
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect(f'/teams/{team_id}/projects/{project_id}/members/')
