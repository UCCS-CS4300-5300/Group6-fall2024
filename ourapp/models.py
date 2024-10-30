import uuid
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


class Review(models.Model):
    reviewID = models.CharField(max_length = 10, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cocktail = models.ForeignKey(Cocktails, related_name="reviews", on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 rating
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cocktail.name} - {self.rating}/5"

    def get_absolute_url(self):
        return reverse("review_detail", args=[str(self.reviewID)])

    def save(self, *args, **kwargs):
        # Generate a unique reviewID if it's a new object
        if not self.reviewID:
            self.reviewID = str(uuid.uuid4())[:10]  # Use the first 10 characters of a UUID
        super().save(*args, **kwargs)


class Meals(models.Model):
    mealID = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200, blank=True, null=True)
    instructions = models.TextField()
    thumbnail = models.URLField()
    ingredients = models.JSONField(null=True, blank=True)
    measurements = models.JSONField(null=True, blank=True)
    reccomended_pairing = models.TextField(null=True)

    @property
    def ingredient_measurements(self):
        return list(zip(self.ingredients, self.measurements))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("meal_detail", args=[str(self.mealID)])

class MealReview(models.Model):
    reviewID = models.CharField(max_length=10, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meals, related_name="reviews", on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 rating
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.meal.name} - {self.rating}/5"

    def save(self, *args, **kwargs):
        # Generate a unique reviewID if it's a new object
        if not self.reviewID:
            self.reviewID = str(uuid.uuid4())[:10]  # Use first 10 characters of UUID
        super().save(*args, **kwargs)

class Profile(models.Model):
    # This line creates a one-to-one relationship between the 
    # Profile model and Django's built-in User model.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # many-to-many relationship with the Cocktails model.
    saved_drinks = models.ManyToManyField('Cocktails', blank=True)
    saved_meals = models.ManyToManyField('Meals', blank=True)

    def __str__(self):
        return self.user.username

# Decorator connects this function to the User model.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# # save the profile whenever the user is saved.
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()