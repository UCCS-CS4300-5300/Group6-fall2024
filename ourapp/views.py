from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from .models import *
import requests
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, CustomAuthenticationForm, ReviewForm
from .models import Profile, Cocktails
from django.contrib import messages


def home_page(request):
    return render(request, 'home.html', {'show_hero': True})

def search_page(request):
    # This view will just render the search page with a form for the search bar
    return render(request, 'search_page.html')

class cocktailDetails(generic.DetailView):
    model = Cocktails
    template_name = 'ourapp/cocktails_detail.html'
    context_object_name = 'cocktails'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['review_form'] = ReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        cocktail = get_object_or_404(Cocktails, pk=self.kwargs['pk'])
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.cocktail = cocktail
            review.save()
            return redirect('Drink_detail', pk=cocktail.pk)
        return self.get(request, *args, **kwargs)
        
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
                        if (search in str(ingrdient).lower()) or (search in str(k.name).lower()):
                            if k not in cocktail_list:
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


def signup(request):
    # Handle the user signup process
    if request.method == 'POST':
        # If the form is submitted, create an instance
        form = SignUpForm(request.POST)
        if form.is_valid():
            # If the form is valid save the user and log them in
            user = form.save()
            login(request, user)
            # Redirect to the home page after successful signup
            return redirect('home_page')
    else:
        # If the request is Get create an empty instance
        form = SignUpForm()
    # Show the signup template with the form
    return render(request, 'ourapp/signup.html', {'form': form})

def user_login(request):
    # Handle the user login process
    if request.method == 'POST':
        # If the form is submitted create an instance
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # If the form is valid get the username and password
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                # If the user is authenticated log them in
                login(request, user)
                # Check if the Remember Me box is checked
                if form.cleaned_data.get('remember_me'):
                    # Set the session to expire to 1 week if checked
                    request.session.set_expiry(604800)  # 1 week in secs.
                # Redirect to the home page after successful login
                return redirect('home_page')
    else:
        # If the request method is Get
        form = CustomAuthenticationForm()
    # Show the login template
    return render(request, 'ourapp/login.html', {'form': form})

# TO DO: Redirect to the login Page when logged out 
@login_required
def user_logout(request):
    # Handle the user logout process
    logout(request)  # Log the user out
    # Redirect to the home page after logging out
    return redirect('home_page')

@login_required
def profile(request):
    # Display the user's profile and their saved drinks 
    saved_drinks = request.user.profile.saved_drinks.all()
    # Show the profile template with the saved drinks
    return render(request, 'ourapp/profile.html', {'saved_drinks': saved_drinks})

@login_required
def save_drink(request, drink_id):
    print("Save drink view called!") 
    # Handle saving a drink to the user's profile
    drink = Cocktails.objects.get(drinkID=drink_id) 
    request.user.profile.saved_drinks.add(drink)
    # Show a message
    messages.success(request, f'{drink.name} has been saved to your profile.')
    # Redirect to the detail page of the saved drink
    return redirect('Drink_detail', pk=drink_id)