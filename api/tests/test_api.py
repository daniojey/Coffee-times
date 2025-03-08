from datetime import date, time, timedelta
from django.utils.timezone import localdate
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from coffeehouses.models import Category, CoffeeHouse, Product, Table
from orders.models import Reservation
from users.models import User




class ProductViewSetsTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(username="supername", password="superpass")
        login_in = self.client.login(username="supername", password="superpass")
        self.assertTrue(login_in, "ProductViewSets not login in")

        self.user_noadmin = User.objects.create_user(username="username",phone='380966344260', password="superpass")

        self.category = Category.objects.create(name="KAVA", slug='kava')

        self.product = Product.objects.create(
            name='Test name',
            description="test description",
            category=self.category,
            price=15.50,
            discount=0.0
        )
        
    
    def test_api_status_code(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_api_product(self):
        response = self.client.get("/api/products/")
        self.assertEqual(len(response.data), 1)
        
        product = response.data[0]

        self.assertEqual(product['name'], 'Test name')
        self.assertEqual(product['adds_by'], self.user.username)
        self.assertEqual(product['category'], self.category.id)
        self.assertEqual(product['price'], '15.50')
        self.assertEqual(product['discount'], '0.00')


    def test_api_product_detail(self):
        product_2 = Product.objects.create(
            name='Test name 2',
            description="test description 2",
            category=self.category,
            price=20.50,
            discount=0.0
        )

        # Проверяем первый продукт
        response = self.client.get(f"/api/products/{self.product.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product = response.data

        self.assertEqual(product['name'], 'Test name')
        self.assertEqual(product['adds_by'], self.user.username)
        self.assertEqual(product['category'], self.category.id)
        self.assertEqual(product['price'], '15.50')
        self.assertEqual(product['discount'], '0.00')

        # Проверяем второй
        response = self.client.get(f"/api/products/{product_2.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product = response.data

        self.assertEqual(product['name'], 'Test name 2')
        self.assertEqual(product['adds_by'], self.user.username)
        self.assertEqual(product['category'], self.category.id)
        self.assertEqual(product['price'], '20.50')
        self.assertEqual(product['discount'], '0.00')


    def test_api_create_product(self):
        data = {
            'name': "Test name 3",
            'description': 'test description 3',
            'category': self.category.id,
            'price': "30.50",
            'discount': "5.50",
        }

        response = self.client.post("/api/products/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product = Product.objects.filter(name="Test name 3").first()
        
        self.assertEqual(product.name, "Test name 3")
        self.assertEqual(product.description, 'test description 3')
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.price, Decimal(30.50))
        self.assertEqual(product.discount, Decimal(5.50))


    def test_api_create_product_invalid_data(self):
        data = {
            # name являеться обязательным полем
            'description': 'test description 4',
            'category': self.category.id,
            'price': "30.50",
            'discount': "5.50",

        }

        response = self.client.post("/api/products/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_api_products_not_admin_user(self):
        self.client.logout()

        loging_in = self.client.login(username="username", password="superpass")
        self.assertTrue(loging_in, "Failed to login in ProductsAPI")

        response = response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    

    def tearDown(self):
        self.product.delete()
        self.category.delete()
        self.user.delete()
        self.user_noadmin.delete()



class ReservationSearchAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="supername", password="superpass")
        login_in = self.client.login(username="supername", password="superpass")
        self.assertTrue(login_in, "Failed to login in ReservationSearchAPITest")

        self.coffeehouse = CoffeeHouse.objects.create(
            name='Coffeehouse test',
            description='test description',
            address='test address 1',
            location={"lat": 51.7558, "lng": 38.6173},
            opening_time=time(hour=7),
            closing_time=time(hour=18)
        )

        self.table = Table.objects.create(
            coffeehouse=self.coffeehouse,
            table_number=1,
            seats=3,
        )

        self.reservation = Reservation.objects.create(
            coffeehouse=self.coffeehouse,
            table=self.table,
            customer_name="Dima",
            customer_phone='380966344260',
            reservation_date = date(year=2025, month=3, day=5),
            reservation_time=time(hour=15, minute=30),
            booking_duration=timedelta(hours=2),
            created_ip='127.0.0.1',
        )

    def test_api_reservation_get(self):
        response = self.client.get(reverse("api:reservation_search"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['reservations']), 0)

    def test_api_post_phone_reservation(self):
        data = {
            "phone": '380966344260',
        }

        response = self.client.post(reverse("api:reservation_search"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        reservation = response.data['reservations'][0]

        self.assertEqual(reservation["coffeehouse_name"], str(self.coffeehouse.name))
        self.assertEqual(reservation['table_number'], self.table.table_number)
        self.assertEqual(reservation['customer_name'], 'Dima')
        self.assertEqual(reservation['customer_phone'], '380966344260')
        self.assertEqual(reservation['reservation_date'], "2025-03-05")
        self.assertEqual(reservation['reservation_time'], "15:30:00")
        self.assertEqual(reservation['booking_duration'], "02:00:00")
        self.assertEqual(reservation['status_display'], "Не успішне")
        self.assertEqual(reservation['streaming_status'], 'Просроченное')
        self.assertEqual(reservation['created_ip'], '127.0.0.1')
        self.assertTrue(reservation['created_at'])

    
    def test_api_post_ivalid_phone(self):
        data = {
            'phone':'345563455642342423'
        }

        response = self.client.post(reverse("api:reservation_search"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Невірний номер телефону, перевірте будь ласка правильність введеного номеру')


    def tearDown(self):
        self.reservation.delete()
        self.table.delete()
        self.coffeehouse.delete()
        self.user.delete()


