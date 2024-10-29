from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Review, MealReview

 # the built-in functions for creating a new user in Django
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text='Required')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
       
class MealReviewForm(forms.ModelForm):
    class Meta:
        model = MealReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars") for i in range(1, 6)]),
            'review_text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your review here...',
                'class': 'form-control'
            }),
        }