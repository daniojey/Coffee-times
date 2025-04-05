from django.core.files import File
from django.db import models
from PIL import Image
from io import BytesIO

class Category(models.Model):
    name = models.CharField(max_length=155, unique=True, verbose_name='Категорія')
    slug = models.SlugField(max_length=200, unique=True,)

    class Meta:
        db_table = 'category'
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'
        ordering = ("id",)

    def __str__(self):
        return self.name


class Product(models.Model):
    image = models.ImageField(upload_to='goods_images', blank=True, null=True, verbose_name='Зображення')
    name = models.CharField(max_length=250, verbose_name="Назва продукту")
    description = models.TextField(blank=True, null=True, verbose_name='Опис')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name='Скидка в %')

    class Meta:
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ("id",)

    def __str__(self):
        return self.name


# Create your models here.
class CoffeeHouse(models.Model):
    image = models.ImageField(upload_to='coffeehouses_images', blank=True, null=True, verbose_name='Зображення')
    name = models.CharField(max_length=155, verbose_name="Назва кав'ярні")
    description = models.CharField(max_length=300, verbose_name='Опис')
    address = models.CharField(max_length=170, verbose_name='Адресса')
    location = models.JSONField(verbose_name="Координаты на карте", blank=True, null=True)  # Для интеграции с API карт
    opening_time = models.TimeField(verbose_name='Час відкриття')
    closing_time = models.TimeField(verbose_name='Час закриття')

    def __str__(self) -> str:
        return self.name
    
    def houseinfo(self):
        return f"{self.name} - {self.address} - {self.opening_time} - {self.closing_time}"
    
    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            
            max_size = (700, 500)
            
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=75)
            output.seek(0)

            self.image = File(output, name=self.image.name)
            
        super().save(*args, **kwargs)
    


class Table(models.Model):
    coffeehouse = models.ForeignKey(CoffeeHouse, on_delete=models.CASCADE,related_name='tables', verbose_name='Кофейня')
    table_number = models.PositiveIntegerField(verbose_name='Номер столика')
    seats = models.PositiveIntegerField(verbose_name='Кількість місць за столиком')

    def __str__(self) -> str:
        return f"Назва кофейні:{self.coffeehouse} - Номер столика:{self.table_number} - Кількість місць:{self.seats}"