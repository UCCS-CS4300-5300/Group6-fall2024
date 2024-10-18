from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class Profile(models.Model):
    # This line creates a one-to-one relationship between the 
    # Profile model and Django's built-in User model.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # many-to-many relationship with the Cocktails model.
    saved_drinks = models.ManyToManyField('Cocktails', blank=True)

    def __str__(self):
        return self.user.username

# Decorator connects this function to the User model.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
# save the profile whenever the user is saved.
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()