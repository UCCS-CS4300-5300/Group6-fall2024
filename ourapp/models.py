from django.db import models
from django.urls import reverse

# Create your models here.

class Cocktails(models.Model):
    drinkID = models.CharField(max_length = 10, primary_key=True)
    name = models.CharField(max_length = 200)
    glass = models.CharField(max_length = 200, blank = True, null = True)
    instructions = models.TextField()
    thumbnail = models.URLField()
    ingredients = models.JSONField(null = True, blank = True)
    measurements = models.JSONField(null = True, blank = True)

    def __str__(self):
        return self.name
    

    def get_absolute_url(self):
        return reverse("Drink_detail", args=[str(self.drinkID)])