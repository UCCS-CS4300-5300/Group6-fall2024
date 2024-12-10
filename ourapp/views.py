from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from .models import Review, Meals, Cocktails, MealReview
from .forms import (ReviewForm,
                    SignUpForm,
                    MealReviewForm,
                    CustomAuthenticationForm)
import requests
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from datetime import datetime
import re
import os
from dotenv import load_dotenv
import ast

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def home_page(request):
    return render(request, 'home.html', {'show_hero': True})


def search_page(request):
    # This view will just render the search page with a form for the search bar
    return render(request, 'search_page.html')


class CocktailDetails(generic.DetailView):
    model = Cocktails
    template_name = 'ourapp/cocktails_detail.html'
    context_object_name = 'cocktails'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        cocktail = self.object
        user = self.request.user
        context = super().get_context_data(**kwargs)
        # Load all reviews linked to this cocktail and add them to the context
        context['reviews'] = Review.objects.filter(cocktail=cocktail)
        # context['reviews'] = self.object.reviews.all()
        context['review_form'] = ReviewForm()

        # Check if the drink is saved in the user's profile
        if user.is_authenticated:
            context['is_saved'] = user.profile.saved_drinks.filter(
                drinkID=cocktail.drinkID).exists()
        else:
            context['is_saved'] = False

        # Split instructions into a list and add to context
        instructions_list = ([instruction.strip() + '.'
                              for instruction in
                              cocktail.instructions.split('.')
                              if instruction.strip()])
        context['instructions_list'] = instructions_list

        return context

    def post(self, request, *args, **kwargs):
        cocktail = get_object_or_404(Cocktails, pk=self.kwargs['pk'])
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.cocktail = cocktail
            review.created_at = datetime.now()
            review.save()
            return redirect('Drink_detail', pk=cocktail.pk)
        return self.get(request, *args, **kwargs)


def search_results(request):
    search = request.GET.get('query', '').lower()  # Normalize case for search

    if search:
        apiURL = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={search}'
        response = requests.get(apiURL)

        if response.status_code == 200:
            data = response.json()
            if data['drinks']:
                cocktail_list = []

                for drink in data['drinks']:
                    ingredients = []
                    measurements = []

                    # Collect ingredients and measurements
                    for i in range(1, 16):
                        ingredient = drink.get(f'strIngredient{i}')
                        measurement = drink.get(f'strMeasure{i}')
                        if ingredient:
                            ingredients.append(ingredient)
                        if measurement:
                            measurements.append(measurement)

                    # Create or update the cocktail in the database
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

                    # Update the cocktail if it already exists
                    if not created:
                        cocktail.ingredients = ingredients
                        cocktail.measurements = measurements
                        cocktail.save()

                # Filter cocktails by search term in name or ingredients
                sips = Cocktails.objects.all()
                for k in sips:
                    for ingredient in k.ingredients:
                        if search in ingredient.lower() or search in k.name.lower():
                            if k not in cocktail_list:
                                cocktail_list.append(k)

                # Check if the request is AJAX
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return render(request,
                                  'search_results.html',
                                  {'cocktails': cocktail_list})

                # Return full page render for non-AJAX requests
                return render(request,
                              'search_page.html',
                              {'drinks': cocktail_list})

            else:
                error_message = 'No Results Found'
        else:
            error_message = 'Failed to retrieve data'

        # Render error messages
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request,
                          'search_results.html',
                          {'error': error_message})
        else:
            return render(request,
                          'search_page.html',
                          {'error': error_message})

    else:
        error_message = 'Please enter a search term'
        return render(request,
                      'search_page.html',
                      {'error': error_message})
    # to anyone who sees this, touch grass


def get_drink_detail(request):
    cocktails = Cocktails.objects.all()
    drinkID_list = []
    for drink in cocktails:
        drinkID = Cocktails.objects.values_list('drinkID',
                                                flat=True).distinct()
        drinkID_list.append(drinkID)
    return render(request,
                  'search_page.html',
                  {'drinkID_list': drinkID_list})


# MEALS
class MealDetails(generic.DetailView):
    model = Meals
    template_name = 'ourapp/meal_detail.html'
    context_object_name = 'meal'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        meal = self.object
        user = self.request.user

        context = super().get_context_data(**kwargs)

        # Split instructions into a list and add to context
        instructions_list = ([instruction.strip() + '.'
                              for instruction
                              in meal.instructions.split('.')
                              if instruction.strip()])
        context['instructions_list'] = instructions_list

        # Combine into pairs
        ingredients_measurements = zip(meal.ingredients, meal.measurements)
        context['ingredients_measurements'] = ingredients_measurements

        # Check if the meal is saved in the user's profile
        if user.is_authenticated:
            context['is_saved'] = (user.
                                   profile.
                                   saved_meals.filter(mealID=meal.mealID).
                                   exists())
        else:
            context['is_saved'] = False

        # Get drink Pairing context
        drink_pairings = drink_pairing_return(meal.mealID)
        context['drink_pairings'] = drink_pairings
        context['MealReviewForm'] = MealReviewForm()
        context['reviews'] = MealReview.objects.filter(meal=meal)


        return context

    def post(self, request, *args, **kwargs):
        meal = self.get_object()
        form = MealReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.meal = meal
            review.created_at = datetime.now()
            review.save()
            return redirect('meal_detail', pk=meal.pk)
        return self.get(request, *args, **kwargs)


def search_meals(request):
    search = request.GET.get('query', '')
    if search:
        apiURL = f'https://www.themealdb.com/api/json/v1/1/search.php?s={search}'
        response = requests.get(apiURL)

        if response.status_code == 200:
            data = response.json()
            if data['meals']:
                for meal in data['meals']:
                    ingredients = []
                    measurements = []

                    for i in range(1, 21):  # MealDB has up to 20 ingredients
                        ingredient = meal.get(f'strIngredient{i}')
                        measurement = meal.get(f'strMeasure{i}')

                        if ingredient and ingredient.strip():
                            ingredients.append(ingredient)
                        if measurement and measurement.strip():
                            measurements.append(measurement)

                    meal_obj, created = Meals.objects.get_or_create(
                        mealID=meal['idMeal'],
                        defaults={
                            'name': meal['strMeal'],
                            'category': meal.get('strCategory'),
                            'area': meal.get('strArea'),
                            'instructions': meal.get('strInstructions'),
                            'thumbnail': meal.get('strMealThumb'),
                            'ingredients': ingredients,
                            'measurements': measurements,
                            # 'reccomended_pairing' : get_chatgpt_response
                            # ('What cocktails pair well with ' +
                            # meal['strMeal'])
                        }
                    )

                    if not created:
                        meal_obj.ingredients = ingredients
                        meal_obj.measurements = measurements
                        # meal_obj.reccomended_pairing =
                        # get_chatgpt_response('What
                        # cocktails pair well with ' + meal['strMeal'])
                        meal_obj.save()

                # Search in database for matches in name or ingredients
                meal_list = []
                meals = Meals.objects.all()
                for meal in meals:
                    if (search.lower() in meal.name.lower() or
                        any(search.lower() in str(ingredient).lower()
                            for ingredient in meal.ingredients)):
                        if meal not in meal_list:
                            meal_list.append(meal)

                # If AJAX
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return render(request,
                                  'ourapp/meal_search_results.html',
                                  {'meals': meal_list})

                return render(request,
                              'ourapp/meal_search.html',
                              {'meals': meal_list})

            else:
                error_message = 'No Results Found'
        else:
            error_message = 'Failed to retrieve data'

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request,
                          'ourapp/meal_search_results.html',
                          {'error': error_message})
        else:
            return render(request,
                          'ourapp/meal_search.html',
                          {'error': error_message})

    else:
        error_message = 'Please enter a search term'
        return render(request,
                      'ourapp/meal_search.html',
                      {'error': error_message})


# def meal_search_results(request):
#     query = request.GET.get('query', '')
#     if query:
#         meals = Meals.objects.filter(name__icontains=query)
#     else:
#         meals = Meals.objects.none()


def get_meal_detail(request):
    # Get all meal objects
    meals = Meals.objects.all()
    # Create a list of meal IDs
    mealID_list = Meals.objects.values_list('mealID', flat=True).distinct()
    return render(request,
                  'meal_search_page.html',
                  {'mealID_list': mealID_list,
                   'meals': meals})


def signup(request):
    # Handle the user signup
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
    saved_meals = request.user.profile.saved_meals.all()
    drink_reviews = Review.objects.filter(user=request.user)
    meal_reviews = MealReview.objects.filter(user=request.user)

    # Show the profile template with the saved drinks
    return render(request, 'ourapp/profile.html', {
        'saved_drinks': saved_drinks,
        'saved_meals': saved_meals,
        'drink_reviews': drink_reviews,
        'meal_reviews': meal_reviews,
    })


@login_required
def save_drink(request, drink_id):
    drink = get_object_or_404(Cocktails, drinkID=drink_id)
    profile = request.user.profile
    # Adds the drink to the user's saved drinks
    profile.saved_drinks.add(drink)
    messages.success(request, f'{drink.name} has been saved to your profile.')
    return redirect('Drink_detail', pk=drink_id)


@login_required
def remove_drink(request, drink_id):
    # print("Remove drink view called")
    drink = get_object_or_404(Cocktails, drinkID=drink_id)
    profile = request.user.profile
    # Removes the drink from the user's saved drinks
    profile.saved_drinks.remove(drink)
    return redirect('Drink_detail', pk=drink_id)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, reviewID=review_id)

    # Ensure only the author can delete their review
    if review.user != request.user:
        return HttpResponseForbidden("""You are
                not allowed to delete this review.""")

    review.delete()
    return redirect('Drink_detail', pk=review.cocktail.drinkID)


@login_required
def save_meal(request, meal_id):
    meal = get_object_or_404(Meals, mealID=meal_id)
    profile = request.user.profile
    profile.saved_meals.add(meal)
    messages.success(request, f'{meal.name} has been saved to your profile.')
    return redirect('meal_detail', pk=meal_id)


@login_required
def remove_meal(request, meal_id):
    meal = get_object_or_404(Meals, mealID=meal_id)
    profile = request.user.profile
    profile.saved_meals.remove(meal)
    messages.success(request,
                     f'{meal.name} has been removed from your profile.')
    return redirect('meal_detail', pk=meal_id)


@login_required
def delete_meal_review(request, review_id):
    review = get_object_or_404(MealReview, reviewID=review_id)

    # Ensure only the author can delete their review
    if review.user != request.user:
        return HttpResponseForbidden("""You are not allowed to
                                     delete this review.""")

    review.delete()
    return redirect('meal_detail', pk=review.meal.mealID)


def update_meal_with_drink_pairing(request, meal_id):
    meal = get_object_or_404(Meals, pk=meal_id)
    meal.reccomended_pairing = get_chatgpt_response("""What cocktail pairs
                                                    well with """ + meal.name)
    meal.save()
    return redirect('meal_detail', pk=meal_id)


def get_chatgpt_response(user_message):
    # Send a message to OpenAI's ChatGPT and return the response.
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",  # or "gpt-3.5-turbo"
        "messages": [{"role": "user", "content": user_message}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        content_text = response.json()["choices"][0]["message"]["content"]
        cocktail_names = re.findall(r"\*\*(.*?)\*\*", content_text)
        cleaned_cocktails = [name.strip() for name in cocktail_names]
        # Join with newlines for bullet points
        #return "\n".join(cleaned_cocktails)
        return cleaned_cocktails
    else:
        print("Error:", response.json())
        return "Error with OpenAI API."

def drink_pairing_return(meal_id):
    #gets the meal to have associated rec. pairing
    meal = get_object_or_404(Meals, pk=meal_id)

    #Cleans the string and makes a list of items not characters
    cleaned_drink_list = clean_drink_names(meal.reccomended_pairing)

    # Fetch all cocktail names in a dictionary for faster lookup
    cocktail_names = {cocktail.name.lower().strip(): cocktail for cocktail in Cocktails.objects.all()}
    print("Cocktail names:", list(cocktail_names.keys()))

    # Initialize a dictionary for results
    drink_items = {}

    # Compare cleaned drinks with normalized cocktail names
    for drink in cleaned_drink_list:
        drink_words = drink.lower().split()  # Split drink into word
        matched_cocktails = [
            #cocktail for cocktail in cocktail_names.values() if drink.lower() in cocktail.name.lower()
            cocktail for cocktail in cocktail_names.values()
            if all(word in cocktail.name.lower() for word in drink_words)  # Match all words
        ]
        if matched_cocktails:
            drink_items[drink] = matched_cocktails

    # Print results for debugging
    print("Drink items:", drink_items)

    return drink_items  # Return results as needed

def clean_drink_names(drink_string):
        # Convert string representation of list to an actual Python list
        try:
            drink_list = ast.literal_eval(drink_string)
        except (ValueError, SyntaxError):
            raise ValueError("Input is not a valid string representation of a list.")
    
        # Initialize a list to store cleaned drink names
        cleaned_drinks = []
    
        for drink in drink_list:
            # Remove unwanted characters, keeping only alphabets and spaces
            cleaned_drink = re.sub(r'[^a-zA-Z\s]', '', drink)
            # Append the cleaned drink name to the list
            cleaned_drinks.append(cleaned_drink.strip())
    
        return cleaned_drinks