import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Player, Team, Game


class BootstrapAuthenticationForm(AuthenticationForm):
    """AuthenticationForm con clases de Bootstrap 5 en los widgets."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
        })
    )


class TeamForm(forms.ModelForm):
    """
    Formulario de Equipo. El campo 'owner' solo debe ser editable por el
    Admin; la vista se encarga de ocultarlo o fijarlo cuando el usuario
    es un Coach.
    """

    class Meta:
        model = Team
        fields = ['name', 'city', 'category', 'owner']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del equipo',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('El nombre del equipo no puede estar vacío.')
        if len(name) < 3:
            raise ValidationError('El nombre del equipo debe tener al menos 3 caracteres.')
        if len(name) > 100:
            raise ValidationError('El nombre del equipo es demasiado largo (máx. 100 caracteres).')
        return name

    def clean_city(self):
        city = self.cleaned_data.get('city', '').strip()
        if not city:
            raise ValidationError('La ciudad no puede estar vacía.')
        if len(city) < 2:
            raise ValidationError('La ciudad debe tener al menos 2 caracteres.')
        return city

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        city = cleaned_data.get('city')
        if name and city:
            qs = Team.objects.filter(name__iexact=name, city__iexact=city)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    'Ya existe un equipo con ese nombre en esa ciudad.'
                )
        return cleaned_data


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'number', 'position', 'birth_date', 'team']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del jugador',
            }),
            'number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '#',
                'min': 0,
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Segunda Base',
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'team': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('El nombre del jugador no puede estar vacío.')
        if len(name) < 2:
            raise ValidationError('El nombre del jugador debe tener al menos 2 caracteres.')
        if len(name) > 100:
            raise ValidationError('El nombre del jugador es demasiado largo (máx. 100 caracteres).')
        return name

    def clean_position(self):
        position = self.cleaned_data.get('position', '').strip()
        if not position:
            raise ValidationError('La posición no puede estar vacía.')
        return position

    def clean_number(self):
        number = self.cleaned_data.get('number')
        if number is None:
            raise ValidationError('El número de dorsal es obligatorio.')
        if number < 0 or number > 99:
            raise ValidationError('El número de dorsal debe estar entre 0 y 99.')
        return number

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date is None:
            raise ValidationError('La fecha de nacimiento no puede estar vacía.')
        if birth_date > datetime.date.today():
            raise ValidationError('La fecha de nacimiento no puede ser una fecha futura.')
        age = (datetime.date.today() - birth_date).days // 365
        if age > 25:
            raise ValidationError('La fecha de nacimiento no es válida para un jugador juvenil.')
        return birth_date

    def clean(self):
        cleaned_data = super().clean()
        team = cleaned_data.get('team')
        name = cleaned_data.get('name')
        number = cleaned_data.get('number')

        if team and number is not None:
            qs = Player.objects.filter(team=team, number=number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f'Ya existe un jugador con el número {number} en este equipo.'
                )

        if team and name:
            qs = Player.objects.filter(team=team, name__iexact=name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f'Ya existe un jugador llamado "{name}" en este equipo.'
                )
        return cleaned_data

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            'home_team',
            'away_team',
            'location',
            'date',
        ]

        widgets = {
            'home_team': forms.Select(attrs={'class': 'form-select'}),
            'away_team': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar del partido'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        home = cleaned_data.get('home_team')
        away = cleaned_data.get('away_team')

        if home and away and home == away:
            raise ValidationError(
                'El equipo local y visitante no pueden ser el mismo.'
            )

        return cleaned_data

class GameScoreForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            'home_score',
            'away_score',
        ]

        widgets = {
            'home_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
            'away_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
        }

    def clean_home_score(self):
        score = self.cleaned_data['home_score']
        if score is not None and score < 0:
            raise ValidationError("El marcador no puede ser negativo.")
        return score

    def clean_away_score(self):
        score = self.cleaned_data['away_score']
        if score is not None and score < 0:
            raise ValidationError("El marcador no puede ser negativo.")
        return score


