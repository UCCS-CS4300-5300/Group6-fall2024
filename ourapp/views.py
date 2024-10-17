from django.shortcuts import render
from django.views import generic
from .models import *
import requests

def home_page(request):
    return render(request, 'home.html', {'show_hero': True})

def search_page(request):
    # This view will just render the search page with a form for the search bar
    return render(request, 'search_page.html')

class cocktailDetails(generic.DetailView):
    model = Cocktails

def search_results(request):
    search = request.GET.get('query','') #Get the input from the search 
    if search:

        apiURL = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={search}' #Append the search term onto the api 
        response = requests.get(apiURL)
        if response.status_code == 200: #If we have connection then get the drinks
            data = response.json()
            if data['drinks']:
                for drink in data['drinks']: #Iterate through the drinks to get the ingredients and measurements

                    ingredients = []
                    measurements = []

                    for i in range(1,16):
                        ingredient = drink.get(f'strIngredient{i}') #Get the ingredients and measurements
                        measurement = drink.get(f'strMeasure{i}')

                        if ingredient:
                            ingredients.append(ingredient)
                        if measurement:
                            measurements.append(measurement)
                        
                    #Check if the cocktail already exists within the database
                    cocktail, created = Cocktails.objects.get_or_create( 
                    drinkID=drink['idDrink'],
                    defaults={
                        'name': drink['strDrink'],
                        'glass': drink.get('strGlass'),
                        'instructions': drink.get('strInstructions'),
                        'thumbnail': drink.get('strDrinkThumb'),
                        'ingredients': ingredients,
                        'measurements': measurements
                    }
                )

                if not created:
                    # Update existing record if necessary
                    cocktail.ingredients = ingredients
                    cocktail.measurements = measurements
                    cocktail.save()
                
                cocktail_list = []
                drink_list=[]
                sips = Cocktails.objects.all()
                for k in sips:
                    for ingrdient in k.ingredients:
                        if search in str(ingrdient).lower():
                            cocktail_list.append(k)
                return render(request, 'search_page.html', {'drinks':cocktail_list}) #Show the results
            else:
                return render(request,'search_page.html',{'error': 'No Results Found'}) #Incase there were no results found
        else: 
            return render(request,'search_page.html',{'error':'Failed to retrieve data'}) #In case the status code was not 200 return error
    else:
        return render(request,'search_page.html',{'error': 'Please enter a search term'}) #If no search term was provided return error

def get_drink_detail(request):
    cocktails = Cocktails.objects.all()
    drinkID_list = []
    for drink in cocktails:
        drinkID = Cocktails.objects.values_list('drinkID', flat=True).distinct()
        drinkID_list.append(drinkID)
    return render( request, 'search_page.html', {'drinkID_list':drinkID_list})

