from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Jugadores (lista pública; alta/edición/baja requieren permisos)
    path('players/', views.player_list, name='player_list'),
    path('players/new/', views.player_create, name='player_create'),
    path('players/<int:pk>/edit/', views.player_update, name='player_update'),
    path('players/<int:pk>/delete/', views.player_delete, name='player_delete'),

    # Equipos (lista pública; alta/edición/baja requieren permisos)
    path('teams/', views.team_list, name='team_list'),
    path('teams/new/', views.team_create, name='team_create'),
    path('teams/<int:pk>/edit/', views.team_update, name='team_update'),
    path('teams/<int:pk>/delete/', views.team_delete, name='team_delete'),

    # Partidos: únicamente de solo lectura para todos los usuarios
    path("games/", views.game_list, name="game_list"),
    path("games/create/", views.game_create, name="game_create"),
    path("games/<int:pk>/edit/", views.game_update, name="game_update"),
    path("games/<int:pk>/score/", views.game_score, name="game_score"),
    path("games/<int:pk>/delete/", views.game_delete, name="game_delete"),
]
