from django.shortcuts import redirect, render

from web.services.client import call


async def home_view(request):
    if not request.session.get('access_token'):
        return redirect('/login/')

    response = await call(request, 'GET', 'core', '/api/users/me/')
    user = response.json()

    return render(request, 'dashboard/home.html', {'user': user})