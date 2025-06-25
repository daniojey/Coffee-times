from datetime import date, datetime, time
from django.utils import timezone
import pytest
from coffeehouses.models import Category, CoffeeHouse, Product, Table
from django.utils.timezone import make_aware
from orders.models import Reservation
from users.models import User

@pytest.fixture
@pytest.mark.django_db
def test_user():
    """Фикстура для создания пользователя"""
    return User.objects.create_user(
        username='user1',
        password="testpass123",
        phone='380966344260',
    )


@pytest.fixture
@pytest.mark.django_db
def product_fabric():
    def _product_fabric(num_products=4):
        category = Category.objects.create(
            name='test_category',
            slug="test_category"
        )

        products = []

        for i in range(num_products):
            product = Product(
                name=f"product {i}",
                description=f'desc {i}',
                category=category,
                price=21.0,
                discount=0.0
            )

            products.append(product)

        created = Product.objects.bulk_create(products)

        return {'category': category, 'products_count': len(created), 'products': created}
    return _product_fabric


@pytest.fixture
@pytest.mark.django_db
def coffeehouse_fabric():
    def _coffeehouse_fabric(count=5):

        coffeehouses = []

        for i in range(count):
            coffee_house = CoffeeHouse(
                name=f"Coffeehouse {i}",
                description=f'desc {i}',
                address=f"Coffeehouse vul.{i}",
                location={"lat": 50.7558, "lng": 32.6173},
                opening_time=time(hour=8).strftime("%H:%M"),
                closing_time=time(hour=20).strftime("%H:%M"),
            )

            coffeehouses.append(coffee_house)

        created = CoffeeHouse.objects.bulk_create(coffeehouses)

        return {"coffeehouses": created}
    
    return _coffeehouse_fabric



@pytest.fixture
@pytest.mark.django_db
def reservation_fabric():
    def _reservation_fabric(user, count=5):
        coffeehouse = CoffeeHouse.objects.create(
            name=f"Coffeehouse test",
            description=f'desc',
            address=f"Coffeehouse test",
            location={"lat": 50.7558, "lng": 32.6173},
            opening_time=time(hour=8).strftime("%H:%M"),
            closing_time=time(hour=20).strftime("%H:%M"),
        )

        table = Table.objects.create(
            coffeehouse=coffeehouse,
            table_number=1,
            seats=4
        )
        
        reservations = []

        for i in range(count):
            res = Reservation(
                coffeehouse=coffeehouse,
                table=table,
                customer_name="Dima",
                customer_phone="380966344260",
                reservation_date=make_aware(datetime(2025, 6, 21, 10, 0)),
                reservation_time=time(hour=10),
                booking_duration=timezone.timedelta(hours=2),
                created_ip='127.0.0.1',
            )

            reservations.append(res)
        
        created = Reservation.objects.bulk_create(reservations)

        return {'reservations': created}
    return _reservation_fabric
