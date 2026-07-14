from django import forms
from .models import Player

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'
        
        # Aquí convertimos la caja de texto en un calendario interactivo
        widgets = {
            'brith_date': forms.DateInput(attrs={'type': 'date'}),
        }