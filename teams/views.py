import asyncio

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from web.services.client import call
from web.services.exceptions import ServiceError
from web.services.pagination import page_context
from web.services.teams import get_my_team_role
from web.services.users import resolve_usernames

MANAGER_ROLES = ('owner', 'admin')


async def teams_list_view(request):
    limit = request.GET.get('limit', 20)
    offset = request.GET.get('offset', 0)

    try:
        response = await call(request, 'GET', 'work', '/api/teams/', params={'limit': limit, 'offset': offset})
    except ServiceError as exc:
        return render(request, 'error.html', {'detail': exc.detail}, status=exc.status_code)

    return render(request, 'teams/list.html', page_context(response.json()))


async def team_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        try:
            response = await call(request, 'POST', 'work', '/api/teams/', json={'name': name, 'description': description})
        except ServiceError as exc:
            return render(request, 'teams/create.html', {'error': exc.detail, 'errors': exc.errors, 'name': name, 'description': description})

        return redirect(f"/teams/{response.json()['id']}/")

    return render(request, 'teams/create.html')


async def team_detail_view(request, team_id):
    team_result, members_result = await asyncio.gather(
        call(request, 'GET', 'work', f'/api/teams/{team_id}/'),
        call(request, 'GET', 'work', f'/api/teams/{team_id}/members/', params={'limit': 100}),
        return_exceptions=True,
    )

    if isinstance(team_result, ServiceError):
        return render(request, 'error.html', {'detail': team_result.detail}, status=team_result.status_code)
    if isinstance(team_result, Exception):
        raise team_result

    members = None
    my_role = None
    if not isinstance(members_result, Exception):
        members = members_result.json()['results']
        usernames = await resolve_usernames(request, [m['user_id'] for m in members])
        for member in members:
            member['username'] = usernames.get(member['user_id'], member['user_id'])
        my_user_id = request.session.get('user_id')
        my_membership = next((m for m in members if m['user_id'] == my_user_id), None)
        my_role = my_membership['role'] if my_membership else None

    return render(request, 'teams/detail.html', {
        'team': team_result.json(),
        'members': members,
        'my_role': my_role,
        'is_manager': my_role in MANAGER_ROLES,
        'is_owner': my_role == 'owner',
    })


async def team_edit_view(request, team_id):
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            try:
                await call(request, 'DELETE', 'work', f'/api/teams/{team_id}/')
            except ServiceError as exc:
                messages.error(request, exc.detail)
                return redirect(f'/teams/{team_id}/edit/')
            return redirect('/teams/')

        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        try:
            await call(request, 'PATCH', 'work', f'/api/teams/{team_id}/', json={'name': name, 'description': description})
        except ServiceError as exc:
            team = {'id': team_id, 'name': name, 'description': description}
            return render(request, 'teams/edit.html', {'error': exc.detail, 'errors': exc.errors, 'team': team})

        return redirect(f'/teams/{team_id}/')

    try:
        response = await call(request, 'GET', 'work', f'/api/teams/{team_id}/')
    except ServiceError as exc:
        return render(request, 'error.html', {'detail': exc.detail}, status=exc.status_code)

    my_role = await get_my_team_role(request, team_id)
    return render(request, 'teams/edit.html', {'team': response.json(), 'is_owner': my_role == 'owner'})


@require_POST
async def team_member_add_view(request, team_id):
    email = request.POST.get('email', '')
    role = request.POST.get('role', '')

    try:
        await call(request, 'POST', 'work', f'/api/teams/{team_id}/members/', json={'email': email, 'role': role})
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect(f'/teams/{team_id}/')


@require_POST
async def team_member_remove_view(request, team_id, user_id):
    try:
        await call(request, 'DELETE', 'work', f'/api/teams/{team_id}/members/{user_id}/')
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect(f'/teams/{team_id}/')


@require_POST
async def team_member_role_view(request, team_id, user_id):
    role = request.POST.get('role', '')

    try:
        await call(request, 'PATCH', 'work', f'/api/teams/{team_id}/members/{user_id}/', json={'role': role})
    except ServiceError as exc:
        messages.error(request, exc.detail)

    return redirect(f'/teams/{team_id}/')


@require_POST
async def team_leave_view(request, team_id):
    try:
        await call(request, 'DELETE', 'work', f'/api/teams/{team_id}/members/me/')
    except ServiceError as exc:
        messages.error(request, exc.detail)
        return redirect(f'/teams/{team_id}/')

    return redirect('/teams/')
