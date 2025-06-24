from django.urls import reverse
from conftest import test_user
import pytest


@pytest.mark.django_db
def test_home_page_view(client, test_user):
    client.login(username='user1', password="testpass123")
    response = client.get(reverse('coffeehouses:index'))
    assert response.status_code == 200