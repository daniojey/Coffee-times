import pytest
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