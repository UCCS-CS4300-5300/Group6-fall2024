from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home_page, name='home_page'),
    path('search/', views.search_page, name='search_page'),
    path('search/results/', views.search_results, name='search_results'),
    path('drink/details/<int:pk>', views.CocktailDetails.as_view(), name='Drink_detail'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('drink/save/<int:drink_id>/', views.save_drink, name='save_drink'),
    path('drink/remove/<int:drink_id>/', views.remove_drink, name='remove_drink'),
    path('review/delete/<str:review_id>/', views.delete_review, name='delete_review'),
    # path('save_drink/<str:drink_id>/', views.save_drink, name='save_drink'), WHY IS THERE 2 SAVE DINRKS??
    path('meal/search/', views.search_meals, name='search_meals'),
    path('meal/search/results/', views.meal_search_results, name='meal_search_results'),
    path('meal/details/<int:pk>', views.MealDetails.as_view(), name='meal_detail'),
    path('meal/save/<str:meal_id>/', views.save_meal, name='save_meal'),
    path('meal/remove/<int:meal_id>/', views.remove_meal, name='remove_meal'),
]