from django.urls import reverse
from coffeehouses.models import Product
from conftest import test_user, product_fabric, coffeehouse_fabric, reservation_fabric
import pytest
import json

# Tests for the homepage


@pytest.mark.django_db
def test_home_page_view(client, test_user, product_fabric):
    """We check that when we go to the page we have a maximum of 4 products 
    loaded and also check that we have the correct template in the answer 
    and the correct status."""

    products_data = product_fabric(num_products=5) 
    response = client.get(reverse('coffeehouses:index'))
    assert response.status_code == 200
    print(response.context)
    assert 'coffeehouses/indextest.html' in [t.name for t in response.templates]
    assert 4 == len(response.context['products'])

# Tests for the MapPage


@pytest.mark.django_db
def test_map_coffehouse_view(client, coffeehouse_fabric):
    """Check the page operation and also check the number 
    of elements in the created JSON representation"""

    coffeehouse_data = coffeehouse_fabric(count=4)

    response = client.get(reverse('coffeehouses:coffee_map'))

    assert response.status_code == 200
    assert len(response.context['coffeehouses']) == 4
    assert len(json.loads(response.context['coffee_shops'])) == 4
    assert 'coffeehouses/map_coffeehouses.html' in [t.name for t in response.templates]

# Tests for the MenuPage


@pytest.mark.django_db
def test_menu_page_view(client, product_fabric):
    products_data = product_fabric(num_products=10)

    response = client.get(reverse('coffeehouses:menu_page'))

    assert response.context['count_products'] == 10
    assert response.context['page_obj'].number == 1
    assert response.context['page_obj'].paginator.num_pages == 3
    assert 'coffeehouses/test_menu_page.html' in [t.name for t in response.templates]

    
    response = client.get(f"{reverse('coffeehouses:menu_page')}?page=2")

    assert response.context['page_obj'].number == 2
    assert response.context['page_obj'].has_next()
    assert response.context['page_obj'].has_previous()

    response = client.get(f"{reverse('coffeehouses:menu_page')}?page=9999999999")

    assert response.status_code == 404
    assert response.context['exception']



# Tests for the ProductPage

@pytest.mark.django_db
def test_product_page_view(client, product_fabric):
    product_data = product_fabric(num_products=1)
    product = product_data['products'][0]

    response = client.get(reverse('coffeehouses:product', args=[product.pk]))

    assert response.status_code == 200
    assert response.context['product'] == product
    assert 'coffeehouses/product.html' in [t.name for t in response.templates]

    response = client.get(reverse('coffeehouses:product', args=[100000]))

    assert response.status_code == 404

    data = {} # null data

    response = client.post(reverse('coffeehouses:product', args=[product.pk]), data=data)

    assert response.status_code == 405


# Tests for the ReservationSearchPage

@pytest.mark.django_db
def test_reservation_search_view(client, test_user, reservation_fabric):
    reservation_data = reservation_fabric(test_user, count=10)
    response = client.get(reverse('coffeehouses:search_number_page'))

    assert response.status_code == 200
    assert len(response.context)

    request_data  = {
        "phone": "380966344260",
    }

    response = client.post(
        reverse('coffeehouses:search_number_page'), 
        data=json.dumps(request_data),  
        content_type='application/json')

    assert len(response.json()['reservations']) == 10
    

    not_valid_data = {}

    response = client.post(
        reverse('coffeehouses:search_number_page'),
        data=json.dumps(not_valid_data),
        content_type='application/json'
    )

    assert response.json()['error']
    assert response.json()['error'] == 'По цьому номеру телефону немає бронювань'