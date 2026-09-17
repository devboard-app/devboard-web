from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('resend-verification/', views.resend_verification_view, name='resend-verification'),
    path('forgot-password/', views.forgot_password_view, name='forgot-password'),
    # These two paths are dictated by devboard-auth's emailed links
    # (settings.FRONTEND_URL + "/auth/verify-email?token=..." etc.) -- not
    # ours to rename.
    path('auth/verify-email/', views.verify_email_view, name='verify-email'),
    path('auth/reset-password/', views.reset_password_view, name='reset-password'),
]