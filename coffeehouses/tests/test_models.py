import pytest
from coffeehouses.models import Category
from django.db.utils import IntegrityError

@pytest.mark.django_db
def test_model_category_create():
    """Создаём экземпляр Category и проверяем параметры"""
    obj = Category.objects.create(
        name="Усі",
        slug="usi"
    )

    assert obj.name == 'Усі'
    assert obj.slug == 'usi'

    with pytest.raises(IntegrityError):
        Category.objects.create(
            name="Усі",
            slug="usi" # уникальное значение
        )