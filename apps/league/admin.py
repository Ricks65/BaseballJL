from django.contrib import admin

from .models import Game, Player, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'category', 'owner')
    list_filter = ('category',)
    search_fields = ('name', 'city')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'position', 'team', 'birth_date')
    list_filter = ('team',)
    search_fields = ('name',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('date', 'home_team', 'away_team', 'home_score', 'away_score', 'location')
    list_filter = ('date',)
