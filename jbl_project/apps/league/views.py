from django.shortcuts import render
from .models import Player
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy  
from .forms import PlayerForm

# Vista para la página principal
def home(request):
    return render(request, 'league/home.html')

# Vista Basada en Clase para la lista de jugadores
class PlayerListView(ListView):
    model = Player
    template_name = 'league/players_list.html'
    context_object_name = 'players'

# ==========================================
# NUEVA VISTA: Para crear un jugador
# ==========================================
class PlayerCreateView(CreateView):
    model = Player
    
    # ¡AQUÍ ESTÁ LA MAGIA! Reemplazamos "fields" por tu nuevo formulario personalizado
    form_class = PlayerForm
    
    template_name = 'league/player_form.html'
    success_url = reverse_lazy('player_list')