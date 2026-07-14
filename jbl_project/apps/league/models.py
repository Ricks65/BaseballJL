from django.db import models

# Create your model# Create your models here.
class Team(models.Model):
    # Defining Categories as a Tuple for a Dropdown menu
    CATEGORY_CHOICES = [
        ('STARTER', 'Starter 6-9'),
        ('JUNIOR', 'Junior 10-13'),
        ('UPPER', 'Upper 14-17'),
        
    ]
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='STARTER'
    )



    def __str__(self):
      return f"{self.name} ({self.get_category_display()})"

class Player(models.Model):
    name = models.CharField(max_length=100)
    number = models.PositiveIntegerField()
    position = models.CharField(max_length=50)
    brith_date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.number}) - {self.position}"
