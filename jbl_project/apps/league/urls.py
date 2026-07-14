from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('players/', views.PlayerListView.as_view(), name='player_list'),
    
    # NUEVA RUTA AQUÍ:
    path('players/new/', views.PlayerCreateView.as_view(), name='player_create'),
]