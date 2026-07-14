from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Team(models.Model):
    CATEGORY_CHOICES = [
        ('STARTER', 'Starter 6-9'),
        ('JUNIOR', 'Junior 10-13'),
        ('UPPER', 'Upper 14-17'),
    ]

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    category = models.CharField(
        max_length=10,
        choices = CATEGORY_CHOICES,
        default = 'STARTER'
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams")

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Player(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    position = models.CharField(max_length=50)
    birth_date = models.DateField()
    # Relationship: 1 Team -> Many Players
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - #{self.number}"

class Game(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    location = models.CharField(max_length=150)
    date = models.DateField()
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.date})"

    @property
    def winner(self):
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None  # empate