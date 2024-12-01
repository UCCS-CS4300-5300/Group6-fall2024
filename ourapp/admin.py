from django.contrib import admin
from .models import Cocktails, Meals, Profile

# Register your models here.
admin.site.register(Cocktails)
admin.site.register(Meals)
admin.site.register(Profile)
