from datetime import time
from django.test import TestCase
from django.urls import reverse_lazy

from coffeehouses.models import CoffeeHouse

class HomePageViewTest(TestCase):
    def setUp(self):
        self.url = reverse_lazy('coffeehouses:index')

    def test_url_response(self):
        reseponse = self.client.get(self.url)

        self.assertEqual(reseponse.status_code, 200)

    def test_template_name(self):
        response = self.client.get(self.url)
        
        self.assertTemplateUsed(response, 'coffeehouses/index.html')


class MapCoffeehouhsesViewTest(TestCase):
    def setUp(self):
        self.coffeehouse = CoffeeHouse.objects.create(
            name='Test kava',
            description='Test description',
            address='pr. Anoskina',
            opening_time=time(hour=14, minute=0),
            closing_time=time(hour=20, minute=30),
        )

    def test_status_code_response(self):
        response = self.client.get(reverse_lazy('coffeehouses:coffee_map'))

        self.assertEqual(response.status_code, 200)

    def test_context_view(self):
        response = self.client.get(reverse_lazy('coffeehouses:coffee_map'))

        self.assertIn('coffee_shops', response.context)
        