from datetime import date, datetime, time, timedelta, timezone
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localtime, now, datetime

from coffeehouses.models import CoffeeHouse, Table
from orders.models import Reservation

class ReservationModelTest(TestCase):
    def setUp(self):
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

    def test_create_reservation(self):

        self.reservation = Reservation.objects.create(
            coffeehouse=self.coffeehouse,
            table=self.table,
            customer_name="danio",
            customer_phone="380966344260",
            reservation_date=date(year=2025, month=1, day=15),
            reservation_time=time(hour=10),
            booking_duration=timedelta(hours=2),
        )

        self.assertEqual(self.reservation.coffeehouse, self.coffeehouse)
        self.assertEqual(self.reservation.table, self.table)
        self.assertEqual(self.reservation.customer_name, "danio")
        self.assertEqual(self.reservation.customer_phone, "380966344260")
        self.assertEqual(self.reservation.reservation_date, date(year=2025, month=1, day=15))
        self.assertEqual(self.reservation.reservation_time, time(hour=10))
        self.assertEqual(self.reservation.booking_duration, timedelta(hours=2))
        self.assertEqual(self.reservation.status, False)
        self.assertEqual(self.reservation.created_ip, "")
        


class CreateReservationTest(TestCase):
    def setUp(self):
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
    
    def test_create_reservation(self):
        data = {
            'coffeehouse': self.coffeehouse.id,
            'table': self.table.id,
            'customer_name': 'Test_name',
            'customer_phone': '380966344260',
            'reservation_date': now().date(),
            'reservation_time': "11:00",
            'booking_duration': "02:00",  # Указание часов таким образом это условие использования кастомного виджета для отображения досутпного времени
        }
        
        response = self.client.get(reverse('orders:reservation'))
        self.assertTemplateUsed(response, 'orders/reservation.html')

        response = self.client.post(reverse('orders:reservation'), data=data)

        # Проверка на ошибки формы
        if response.context and 'form' in response.context:
            form = response.context['form']
            if not form.is_valid():
                print("Ошибки формы:", form.errors)  # Вывод всех ошибок формы для диагностики\

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reservation.objects.filter(customer_name='Test_name').exists())

        self.assertRedirects(response, reverse("coffeehouses:index"))


        reservation = Reservation.objects.get(customer_name='Test_name')

        print(reservation.coffeehouse)
        print(reservation.table)
        print(reservation.customer_name)
        print(reservation.customer_phone)
        print(reservation.reservation_date)
        print(reservation.reservation_time)
        print(reservation.booking_duration)
        print(reservation.created_ip)
        print(reservation.status)

        self.assertEqual(reservation.coffeehouse, self.coffeehouse)
        self.assertEqual(reservation.table, self.table)
        self.assertEqual(reservation.customer_name, 'Test_name')
        self.assertEqual(reservation.customer_phone, '380966344260')
        self.assertEqual(reservation.reservation_date, now().date())
        self.assertEqual(reservation.reservation_time, time(hour=11))
        self.assertEqual(reservation.booking_duration, timedelta(hours=2))
        self.assertEqual(reservation.status, False)
        self.assertEqual(reservation.created_ip, '127.0.0.1')