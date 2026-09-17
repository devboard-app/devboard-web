from django.urls import path

from . import views

urlpatterns = [
    path('teams/<uuid:team_id>/projects/<uuid:project_id>/', views.project_detail_view, name='project-detail'),
]
