from datetime import date, time, timedelta
from django.utils.timezone import localdate, now
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers import ReservationProfileSericalizer
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


class ProfileinfoAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Dima", password="123pass")
        login_in = self.client.login(username="Dima", password="123pass")
        self.assertTrue(login_in, "Failed to login in ProfileinfoAPITest")

        date_now = now()
        self.date_late = date_now + timedelta(days=1)


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

        self.actual_reservation = Reservation.objects.create(
            coffeehouse=self.coffeehouse,
            table=self.table,
            customer_name="Dima",
            customer_phone='380966344260',
            reservation_date = self.date_late.date(),
            reservation_time=time(hour=16),
            booking_duration=timedelta(hours=2),
            created_ip='127.0.0.1',
        )

    
    def test_api_status_code_return(self):
        response = self.client.get(reverse("api:user_profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_status_code_not_login_user(self):
        self.client.logout()
        response = self.client.get(reverse("api:user_profile"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_api_result_data(self):
        response = self.client.get(reverse("api:user_profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data['reservations'])
        self.assertTrue(response.data['actual_reservations'])    

        res_data = {
                            'coffeehouse_name': 'Coffeehouse test',
                            'reservation_date': '2025-03-05', 
                            'reservation_time': '15:30:00', 
                            'status_res': 'Просроченное'
                        }
        
        actual_res_data = {
                            'coffeehouse_name': 'Coffeehouse test', 
                            'reservation_date': self.date_late.strftime('%Y-%m-%d'), 
                            'reservation_time': '16:00:00', 
                            'status_res': 'Актуальное'
                        }

        self.assertIn(res_data, response.data['reservations'])
        self.assertIn(actual_res_data, response.data['actual_reservations'])

    def test_api_post(self):
        data = {
            'phone': "gfdsgfsgsfgsg",
        }

        response= self.client.post(reverse("api:user_profile"), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def tearDown(self):
        self.actual_reservation.delete()
        self.reservation.delete()
        self.table.delete()
        self.coffeehouse.delete()
        self.user.delete()


class ProfileHistoryAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Dima", password="testpass")
        login_in = self.client.login(username="Dima", password="testpass")
        self.assertTrue(login_in, "Failed to login in ProfileHistoryAPITest")

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
            reservation_date = date(year=2024, month=3, day=5),
            reservation_time=time(hour=15, minute=30),
            booking_duration=timedelta(hours=2),
            created_ip='127.0.0.1',
        )

        self.reservation_2 = Reservation.objects.create(
            coffeehouse=self.coffeehouse,
            table=self.table,
            customer_name="Dima",
            customer_phone='380966344260',
            reservation_date = date(year=2024, month=4, day=5),
            reservation_time=time(hour=15, minute=30),
            booking_duration=timedelta(hours=2),
            created_ip='127.0.0.1',
        )

        self.reservation_3 = Reservation.objects.create(
            coffeehouse=self.coffeehouse,
            table=self.table,
            customer_name="Dima",
            customer_phone='380966344260',
            reservation_date = date(year=2024, month=5, day=5),
            reservation_time=time(hour=15, minute=30),
            booking_duration=timedelta(hours=2),
            created_ip='127.0.0.1',
        )


    def test_api_status_code(self):
        response = self.client.get(reverse("api:user_history_reservations"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_not_login_status_code(self):
        self.client.logout()
        response = self.client.get(reverse("api:user_history_reservations"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_api_post_request(self):
        data = {
            'phone': ' fgdhdgfhghdf'
        }

        response = self.client.post(reverse("api:user_history_reservations"), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_result_data(self):
        response = self.client.get(reverse('api:user_history_reservations'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res_data = {
            'coffeehouse_name': 'Coffeehouse test',
            'reservation_date': '2024-03-05', 
            'reservation_time': '15:30:00', 
            'status_res': 'Просроченное',
        }

        res_2_data = {
            'coffeehouse_name': 'Coffeehouse test',
            'reservation_date': '2024-04-05', 
            'reservation_time': '15:30:00', 
            'status_res': 'Просроченное',
        }

        res_3_data = {
            'coffeehouse_name': 'Coffeehouse test',
            'reservation_date': '2024-05-05', 
            'reservation_time': '15:30:00', 
            'status_res': 'Просроченное',
        }

        self.assertTrue(response.data['results'])
        self.assertEqual(response.data['count'], 3)

        self.assertIn(res_data, response.data['results'])
        self.assertIn(res_2_data, response.data['results'])
        self.assertIn(res_3_data, response.data['results'])


    def test_api_page_size_2(self):
        response = self.client.get(f"{reverse('api:user_history_reservations')}?page_size=2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data['next'])

        expected_url = "http://testserver/api/v1/user_history_reservations/?page=2&page_size=2"
        url = response.data['next']

        self.assertEqual(expected_url, url)

        self.assertEqual(response.data['previous'], None)

    def tearDown(self):
        self.reservation_3.delete()
        self.reservation_2.delete()
        self.reservation.delete()
        self.coffeehouse.delete()
        self.table.delete()
        self.user.delete()


class CreateReservationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Dima", password="testpass")
        login_in = self.client.login(username="Dima", password="testpass")
        self.assertTrue(login_in, "Failed to login in ProfileHistoryAPITest")

        date_now = now()
        self.date_late = date_now + timedelta(days=1)

        self.coffeehouse = CoffeeHouse.objects.create(
            id=1,
            name='Coffeehouse test',
            description='test description',
            address='test address 1',
            location={"lat": 51.7558, "lng": 38.6173},
            opening_time=time(hour=7),
            closing_time=time(hour=18)
        )

        self.table = Table.objects.create(
            id=1,
            coffeehouse=self.coffeehouse,
            table_number=1,
            seats=3,
        )

    def test_api_get(self):
        response = self.client.get(reverse('api:create_reservation'))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_api_create_reservation_valid_data(self):
        data = {
            "coffeehouse": 1,
            'table': 1,
            'customer_name': "Dima",
            'customer_phone': '380966344260',
            'reservation_date': self.date_late.strftime('%Y-%m-%d'),
            'reservation_time': '15:00:00',
            'booking_duration': '00:30:00',
        }

        response = self.client.post(reverse('api:create_reservation'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(response.data['message'])
        self.assertTrue(response.data['reservation'])
        
        res_data = response.data['reservation']

        self.assertEqual(response.data['message'], 'Бронирование успешно созданно')

        self.assertEqual(res_data['coffeehouse'], 1)
        self.assertEqual(res_data['table'], 1)
        self.assertEqual(res_data['customer_name'], "Dima")
        self.assertEqual(res_data['customer_phone'], '380966344260')
        self.assertEqual(res_data['reservation_date'], self.date_late.strftime('%Y-%m-%d'))
        self.assertEqual(res_data['reservation_time'], '15:00:00')
        self.assertEqual(res_data['booking_duration'], '00:30:00')

    def test_api_create_invalid_data(self):
        data_id = {
            "coffeehouse": 2,
            'table': 2,
            'customer_name': "Dima",
            'customer_phone': '380966344260',
            'reservation_date': self.date_late.strftime('%Y-%m-%d'),
            'reservation_time': '15:00:00',
            'booking_duration': '00:30:00',
        }        

        data_phone = {
            "coffeehouse": 1,
            'table': 1,
            'customer_name': "Dima",
            'customer_phone': '6435645966344260',
            'reservation_date': self.date_late.strftime('%Y-%m-%d'),
            'reservation_time': '15:00:00',
            'booking_duration': '00:30:00',
        }

        response = self.client.post(reverse('api:create_reservation'), data_id, format='json')

        res_data = response.data

        self.assertEqual(res_data['coffeehouse'][0].title(), 'Недопустимый Первичный Ключ "2" - Объект Не Существует.')
        self.assertEqual(res_data['table'][0].title(), 'Недопустимый Первичный Ключ "2" - Объект Не Существует.')


        response = self.client.post(reverse('api:create_reservation'), data_phone, format='json')

        res_data = response.data

        self.assertEqual(res_data['customer_phone'][0].title(), 'Убедитесь, Что Это Значение Содержит Не Более 15 Символов.')

    def tearDown(self):
        self.table.delete()
        self.coffeehouse.delete()
        self.user.delete()