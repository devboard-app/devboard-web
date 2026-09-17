from django.urls import path

from . import views

urlpatterns = [
    path('teams/<uuid:team_id>/projects/', views.project_list_view, name='project-list'),
    path('teams/<uuid:team_id>/projects/create/', views.project_create_view, name='project-create'),
    path('teams/<uuid:team_id>/projects/<uuid:project_id>/', views.project_detail_view, name='project-detail'),
    path('teams/<uuid:team_id>/projects/<uuid:project_id>/edit/', views.project_edit_view, name='project-edit'),
    path('teams/<uuid:team_id>/projects/<uuid:project_id>/members/', views.project_members_view, name='project-members'),
    path('teams/<uuid:team_id>/projects/<uuid:project_id>/members/add/', views.project_member_add_view, name='project-member-add'),
    path('teams/<uuid:team_id>/projects/<uuid:project_id>/members/<uuid:user_id>/remove/', views.project_member_remove_view, name='project-member-remove'),
    path('teams/<uuid:team_id>/projects/<uuid:project_id>/members/<uuid:user_id>/role/', views.project_member_role_view, name='project-member-role'),
]
