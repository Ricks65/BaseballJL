"""
URL configuration for jbl_project project.

See: https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('league/', include('apps.league.urls')),
]
