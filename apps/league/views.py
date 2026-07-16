from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import (BootstrapAuthenticationForm, PlayerForm, TeamForm, GameForm, GameScoreForm,)
from .models import Game, Player, Team


# =============================================================================
# Helpers de permisos
# =============================================================================
def is_admin(user):
    """El Admin es el Superuser."""
    return user.is_authenticated and user.is_superuser


def is_coach(user):
    """El Coach es un usuario Staff (no superuser)."""
    return user.is_authenticated and user.is_staff and not user.is_superuser


def coach_team(user):
    """Devuelve el equipo del cual el Coach es owner, o None."""
    return Team.objects.filter(owner=user).first()


def can_edit_team(user, team):
    if is_admin(user):
        return True
    if is_coach(user):
        return team.owner_id == user.id
    return False


def can_manage_player(user, player):
    if is_admin(user):
        return True
    if is_coach(user):
        return player.team.owner_id == user.id
    return False


# =============================================================================
# AUTENTICACIÓN
# =============================================================================
class MyLoginView(LoginView):
    template_name = 'league/login.html'
    form_class = BootstrapAuthenticationForm
    next_page = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        display_name = user.first_name or user.username
        messages.success(self.request, f'Bienvenido, {display_name}')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)


# =============================================================================
# INFORMACIÓN PÚBLICA / DASHBOARD
# =============================================================================
def home(request):
    """
    Vista pública. No requiere inicio de sesión.
    Muestra información de la liga, del deporte y estadísticas generales.
    """
    games_played = Game.objects.filter(
        home_score__isnull=False, away_score__isnull=False
    ).count()

    context = {
        'league_name': getattr(settings, 'LEAGUE_NAME', 'Junior Baseball League'),
        'league_sport': getattr(settings, 'LEAGUE_SPORT', 'Béisbol'),
        'league_founded_year': getattr(settings, 'LEAGUE_FOUNDED_YEAR', 2024),
        'league_description': getattr(settings, 'LEAGUE_DESCRIPTION', ''),
        'team_count': Team.objects.count(),
        'player_count': Player.objects.count(),
        'game_count': Game.objects.count(),
        'games_played': games_played,
        'recent_games': Game.objects.select_related(
            'home_team', 'away_team'
        ).order_by('-date')[:5],
    }
    return render(request, 'league/home.html', context)


# =============================================================================
# EQUIPOS
# =============================================================================
@login_required
def team_list(request):

    if request.user.is_superuser:
        teams = Team.objects.select_related("owner").all()

    elif request.user.is_staff:
        teams = Team.objects.select_related("owner").filter(
            owner=request.user
        )

    else:
        teams = Team.objects.none()

    return render(
        request,
        "league/teams/team_list.html",
        {
            "teams": teams
        }
    )


@login_required(login_url='/league/login/')
def team_create(request):
    """Solo el Admin puede crear equipos."""
    if not is_admin(request.user):
        return HttpResponseForbidden(
            'No tienes permiso para crear equipos.'
        )
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo creado correctamente.')
            return redirect('team_list')
    else:
        form = TeamForm()
    return render(
        request, 'league/teams/team_form.html',
        {'form': form, 'title': 'Nuevo equipo'}
    )


@login_required(login_url='/league/login/')
def team_update(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not can_edit_team(request.user, team):
        return HttpResponseForbidden(
            'No tienes permiso para editar este equipo.'
        )
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            updated_team = form.save(commit=False)
            # Un Coach no puede reasignar el owner del equipo
            if not is_admin(request.user):
                updated_team.owner = team.owner
            updated_team.save()
            messages.success(request, 'Equipo actualizado correctamente.')
            return redirect('team_list')
    else:
        form = TeamForm(instance=team)
    return render(
        request, 'league/teams/team_form.html',
        {'form': form, 'title': 'Editar equipo'}
    )


@login_required(login_url='/league/login/')
def team_delete(request, pk):
    """Solo el Admin puede eliminar equipos."""
    team = get_object_or_404(Team, pk=pk)
    if not is_admin(request.user):
        return HttpResponseForbidden(
            'No tienes permiso para eliminar equipos.'
        )
    if request.method == 'POST':
        team.delete()
        messages.success(request, 'Equipo eliminado correctamente.')
        return redirect('team_list')
    return render(request, 'league/teams/team_confirm_delete.html', {'team': team})


# =============================================================================
# JUGADORES
# =============================================================================
@login_required
def player_list(request):

    if request.user.is_superuser:

        players = Player.objects.select_related(
            "team",
            "team__owner"
        ).all()

    elif request.user.is_staff:

        players = Player.objects.select_related(
            "team",
            "team__owner"
        ).filter(
            team__owner=request.user
        )

    else:

        players = Player.objects.none()

    return render(
        request,
        "league/players/player_list.html",
        {
            "players": players
        }
    )


@login_required(login_url='/league/login/')
def player_create(request):
    if not (is_admin(request.user) or is_coach(request.user)):
        return HttpResponseForbidden(
            'No tienes permiso para crear jugadores.'
        )

    team_for_coach = None
    if is_coach(request.user):
        team_for_coach = coach_team(request.user)
        if team_for_coach is None:
            messages.error(request, 'No tienes un equipo asignado.')
            return redirect('player_list')

    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if is_coach(request.user):
            # Forzamos el equipo del Coach antes de validar duplicados
            form.data = form.data.copy()
            form.data['team'] = team_for_coach.pk
        if form.is_valid():
            player = form.save(commit=False)
            if is_coach(request.user):
                player.team = team_for_coach
            player.save()
            messages.success(request, 'Jugador creado correctamente.')
            return redirect('player_list')
    else:
        initial = {'team': team_for_coach.pk} if team_for_coach else {}
        form = PlayerForm(initial=initial)
        if is_coach(request.user):
            form.fields['team'].queryset = Team.objects.filter(pk=team_for_coach.pk)
            form.fields['team'].disabled = True

    return render(
        request, 'league/players/player_form.html',
        {'form': form, 'title': 'Nuevo jugador'}
    )


@login_required(login_url='/league/login/')
def player_update(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if not can_manage_player(request.user, player):
        return HttpResponseForbidden(
            'No tienes permiso para editar este jugador.'
        )

    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if is_coach(request.user):
            form.data = form.data.copy()
            form.data['team'] = player.team_id
        if form.is_valid():
            updated_player = form.save(commit=False)
            # Un Coach no puede cambiar el equipo del jugador
            if is_coach(request.user):
                updated_player.team = player.team
            updated_player.save()
            messages.success(request, 'Jugador actualizado correctamente.')
            return redirect('player_list')
    else:
        form = PlayerForm(instance=player)
        if is_coach(request.user):
            form.fields['team'].queryset = Team.objects.filter(pk=player.team_id)
            form.fields['team'].disabled = True

    return render(
        request, 'league/players/player_form.html',
        {'form': form, 'title': 'Editar jugador'}
    )


@login_required(login_url='/league/login/')
def player_delete(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if not can_manage_player(request.user, player):
        return HttpResponseForbidden(
            'No tienes permiso para eliminar este jugador.'
        )
    if request.method == 'POST':
        player.delete()
        messages.success(request, 'Jugador eliminado correctamente.')
        return redirect('player_list')
    return render(
        request, 'league/players/player_confirm_delete.html', {'player': player}
    )


# =============================================================================
# PARTIDOS (solo lectura para todos los roles, según la rúbrica)
# =============================================================================
def game_list(request):
    games = Game.objects.select_related('home_team', 'away_team').order_by('-date')

    return render(
        request,
        'league/games/game_list.html',
        {'games': games})

@login_required
def game_create(request):

    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para crear partidos.")
        return redirect("game_list")

    if request.method == "POST":
        form = GameForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Partido creado correctamente.")
            return redirect("game_list")

    else: form = GameForm()

    return render(request, "league/games/game_form.html", {"form": form, "title": "Nuevo Partido"})

@login_required
def game_update(request, pk):

    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso.")
        return redirect("game_list")

    game = get_object_or_404(Game, pk=pk)

    if request.method == "POST":
        form = GameForm(request.POST, instance=game)

        if form.is_valid():
            form.save()
            messages.success(request, "Partido actualizado.")
            return redirect("game_list")

    else:
        form = GameForm(instance=game)

    return render(
        request,
        "league/games/game_score_form.html",
        {"form": form,"title": "Editar Partido"})

@login_required
def game_delete(request, pk):

    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso.")
        return redirect("game_list")

    game = get_object_or_404(Game, pk=pk)

    if request.method == "POST":
        game.delete()
        messages.success(request, "Partido eliminado.")
        return redirect("game_list")

    return render(request, "league/games/game_confirm_delete.html", {"game": game})

@login_required
def game_score(request, pk):

    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para modificar resultados.")
        return redirect("game_list")

    game = get_object_or_404(Game, pk=pk)

    if request.method == "POST":
        form = GameScoreForm(request.POST, instance=game)

        if form.is_valid():
            form.save()
            messages.success(request, "Marcador actualizado correctamente.")
            return redirect("game_list")

    else:
        form = GameScoreForm(instance=game)

    return render(
        request,
        "league/games/game_score_form.html",
        {
            "form": form,
            "game": game,
            "title": "Actualizar Marcador",
        },
    )

def crear_admin_temporal(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin','admin@test.com','admin123')
        return HttpResponse("<h1>Usuario Admin creado correctamente.</h1>")
    else:
        return HttpResponse("<h1>El usuario Admin ya existe.</h1>")




