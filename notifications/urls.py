from django.urls import path

from . import views

urlpatterns = [
    path('notifications/', views.notifications_list_view, name='notification-list'),
    path('notifications/read-all/', views.notification_mark_all_read_view, name='notification-mark-all-read'),
    path('notifications/<uuid:notification_id>/read/', views.notification_mark_read_view, name='notification-mark-read'),
    path('notifications/<uuid:notification_id>/delete/', views.notification_delete_view, name='notification-delete'),
]
