from django.urls import path

from . import views

urlpatterns = [
    path('teams/', views.teams_list_view, name='team-list'),
    path('teams/create/', views.team_create_view, name='team-create'),
    path('teams/<uuid:team_id>/', views.team_detail_view, name='team-detail'),
    path('teams/<uuid:team_id>/edit/', views.team_edit_view, name='team-edit'),
    path('teams/<uuid:team_id>/leave/', views.team_leave_view, name='team-leave'),
    path('teams/<uuid:team_id>/members/add/', views.team_member_add_view, name='team-member-add'),
    path('teams/<uuid:team_id>/members/<uuid:user_id>/remove/', views.team_member_remove_view, name='team-member-remove'),
    path('teams/<uuid:team_id>/members/<uuid:user_id>/role/', views.team_member_role_view, name='team-member-role'),
]
