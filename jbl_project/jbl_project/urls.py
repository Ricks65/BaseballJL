# jbl_project/urls.py

from django.contrib import admin
from django.urls import path, include
from apps.league import views

urlpatterns = [
    path ('',views.home, name='home'),
    path ('players/', views.PlayerListView.as_view(), name='player_list'),

   path('admin/', admin.site.urls),
    # Aquí le decimos: "Todo lo que empiece con league/, mándalo a la app league"
  path('league/', include('apps.league.urls')), 
]