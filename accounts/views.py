from django.shortcuts import redirect, render

from accounts.services import (
    forgot_password,
    login,
    logout,
    register,
    resend_verification,
    reset_password,
    verify_email,
)
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

async def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        try:
            await register(request, email, password)
        except ServiceError as exc:
            return render(request, 'accounts/register.html', {'error': exc.detail, 'errors': exc.errors, 'email': email})

        return render(request, 'accounts/register_done.html')

    return render(request, 'accounts/register.html')

async def verify_email_view(request):
    token = request.GET.get('token', '')

    try:
        await verify_email(request, token)
    except ServiceError as exc:
        return render(request, 'accounts/verify_email.html', {'error': exc.detail})

    return render(request, 'accounts/verify_email.html', {'verified': True})

async def resend_verification_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        try:
            await resend_verification(request, email)
        except ServiceError as exc:
            return render(request, 'accounts/resend_verification.html', {'error': exc.detail, 'errors': exc.errors, 'email': email})

        return render(request, 'accounts/resend_verification.html', {'sent': True})

    return render(request, 'accounts/resend_verification.html')

async def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        try:
            await forgot_password(request, email)
        except ServiceError as exc:
            return render(request, 'accounts/forgot_password.html', {'error': exc.detail, 'errors': exc.errors, 'email': email})

        return render(request, 'accounts/forgot_password.html', {'sent': True})

    return render(request, 'accounts/forgot_password.html')

async def reset_password_view(request):
    token = request.GET.get('token', '') or request.POST.get('token', '')

    if request.method == 'POST':
        password = request.POST.get('password', '')

        try:
            await reset_password(request, token, password)
        except ServiceError as exc:
            return render(request, 'accounts/reset_password.html', {'error': exc.detail, 'errors': exc.errors, 'token': token})

        return redirect('/login/')

    return render(request, 'accounts/reset_password.html', {'token': token})