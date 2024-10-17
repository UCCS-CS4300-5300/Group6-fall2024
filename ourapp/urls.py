from django.urls import path
from .views import home_page
from . import views

urlpatterns = [
    path('', home_page, name='home_page'),
    path('search/', views.search_page, name='search_page'),
    path('search/results/', views.search_results, name='search_results'),
    path('drink/details/<int:pk>', views.cocktailDetails.as_view(), name='Drink_detail'),
]