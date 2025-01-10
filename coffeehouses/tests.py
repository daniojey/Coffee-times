from datetime import date, time, timedelta
import json
from unicodedata import category
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from coffeehouses.models import Category, CoffeeHouse, Product, Table
from orders.models import Reservation

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


class MenuPageViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='KAVA',
            slug='kava',
        )

        self.product = Product.objects.create(
            name='Test product',
            description='Test desription',
            category=self.category,
            price=33.00
        )

    def test_check_status_code_response(self):
        response = self.client.get(reverse_lazy('coffeehouses:menu_page'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "coffeehouses/menu_page.html")
    
    def test_check_context_in_response(self):
        response = self.client.get(reverse_lazy('coffeehouses:menu_page'))

        self.assertIn('page_obj', response.context)
        self.assertIn('products', response.context)

        self.assertIn(self.product, response.context['products'])


class ProductViewTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name='KAVA',
            slug='kava',
        )

        self.product = Product.objects.create(
            name='Test product',
            description='Test desription',
            category=self.category,
            price=33.00
        )

    
    def test_reponse_status_code(self):
        response = self.client.get(reverse_lazy('coffeehouses:product', args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'coffeehouses/product.html')

    def test_context_view(self):
        response = self.client.get(reverse_lazy('coffeehouses:product', args=[self.product.pk]))

        self.assertIn('product', response.context)

        self.assertEqual(self.product, response.context['product'])

    def test_404_product_is_none(self):
        response = self.client.get(reverse_lazy('coffeehouses:product', args=[123467890]))

        self.assertEqual(response.status_code, 404)


class ReservationSearchViewTest(TestCase):
    def setUp(self):
        self.coffeehouse = CoffeeHouse.objects.create(
            name='Test coffeehouse',
            description='test description',
            address='test address 7a',
            opening_time=time(hour=8, minute=0),
            closing_time=time(hour=18, minute=30),
        )


        self.table = Table.objects.create(
            coffeehouse=self.coffeehouse,
            table_number=1,
            seats=4,
        )

        self.reservation = Reservation.objects.create(
            coffeehouse=self.coffeehouse,
            table=self.table,
            customer_name = "testname",
            customer_phone='380966344260',
            reservation_date = date(year=2025, month=1, day=5),
            reservation_time = time(hour=15, minute=30),
            booking_duration=timedelta(hours=2),
            created_ip='127.0.0.1',
        )

    def test_response_url_check(self):
        response = self.client.get(reverse_lazy('coffeehouses:search_number_page'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coffeehouses/search_number_page.html')

    def test_post_request_valid_phone(self):
        data = {'phone': '380966344260'}
        response = self.client.post(
            reverse("coffeehouses:search_number_page"),
            data=json.dumps(data),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = response.json()
        self.assertIn('reservations', response_data)
        self.assertEqual(len(response_data['reservations']), 1)
        reservation_one = response_data['reservations'][0]

        self.assertEqual(reservation_one['table_number'], self.reservation.table.table_number)
        self.assertEqual(reservation_one['seats'], self.table.seats)

    def test_post_request_not_valid_phone(self):
        data = {'phone': '0555345345345341231342342342'}
        response = self.client.post(
            reverse("coffeehouses:search_number_page"),
            data=json.dumps(data),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Невірний формат номеру телефону, перевірте  формат введеного номеру')

    
    def test_post_request_not_phone_data(self):
        data = {}
        response = self.client.post(
            reverse("coffeehouses:search_number_page"),
            data=json.dumps(data),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'По цьому номеру телефону немає бронювань')
