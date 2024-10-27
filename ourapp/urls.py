from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home_page, name='home_page'),
    path('search/', views.search_page, name='search_page'),
    path('search/results/', views.search_results, name='search_results'),
    path('drink/details/<int:pk>', views.cocktailDetails.as_view(), name='Drink_detail'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('save_drink/<str:drink_id>/', views.save_drink, name='save_drink'),
]