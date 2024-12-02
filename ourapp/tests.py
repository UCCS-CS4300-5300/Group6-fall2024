from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Cocktails, Review
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By


# Create your tests here.
class HomepageTests(TestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("home_page"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("home_page"))
        self.assertTemplateUsed(response, "home.html")

    def test_template_content(self):
        response = self.client.get(reverse("home_page"))
        self.assertContains(response,
                            '''<h2>Elevate Your Culinary
                            Skills With Drink Pairings</h2>''')
        self.assertNotContains(response, "Not on the page")


class ReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass')
        self.cocktail = Cocktails.objects.create(
            drinkID="12345",
            name="Test Cocktail",
            instructions="Mix and serve",
            thumbnail="https://example.com/image.jpg"
        )

    def test_add_review(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/drink/details/{self.cocktail.pk}', {
            'rating': 5,
            'review_text': 'Excellent drink!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, 'Excellent drink!')

    def test_view_reviews(self):
        Review.objects.create(user=self.user,
                              cocktail=self.cocktail,
                              rating=4, review_text="Great!")
        response = self.client.get(f'/drink/details/{self.cocktail.pk}')
        self.assertContains(response, "Great!")
        self.assertContains(response, "4")
