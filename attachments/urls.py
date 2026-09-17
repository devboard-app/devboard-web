from django.urls import path

from . import views

urlpatterns = [
    path('api/attachments/request-upload/', views.request_upload_view, name='attachment-request-upload'),
    path('api/attachments/<uuid:attachment_id>/confirm/', views.confirm_upload_view, name='attachment-confirm'),
    path('attachments/upload-test/', views.upload_widget_test_view, name='attachment-upload-test'),
]
