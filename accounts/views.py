from django.shortcuts import redirect, render

from accounts.services import login, logout
from web.services.exceptions import ServiceError


async def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            await login(request, email, password)
        except ServiceError as exc:
            return render(request, 'accounts/login.html', {'error': exc.detail})

        return redirect('/')

    return render(request, 'accounts/login.html')

async def logout_view(request):
    if request.method == 'POST':
        await logout(request)
    return redirect('/')