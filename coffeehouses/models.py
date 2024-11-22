from django.db import models

# Create your models here.
class CoffeeHouse(models.Model):
    name = models.CharField(max_length=155, verbose_name='Назва кофейни')
    description = models.CharField(max_length=300, verbose_name='Опис')
    address = models.CharField(max_length=170, verbose_name='Адресса')
    location = models.JSONField(verbose_name="Координаты на карте", blank=True, null=True)  # Для интеграции с API карт
    opening_time = models.TimeField(verbose_name='Час відкриття')
    closing_time = models.TimeField(verbose_name='Час закриття')

    def __str__(self) -> str:
        return self.name
    
    def houseinfo(self):
        return f"{self.name} - {self.address} - {self.opening_time} - {self.closing_time}"
    


class Table(models.Model):
    coffeehouse = models.ForeignKey(CoffeeHouse, on_delete=models.CASCADE,related_name='tables', verbose_name='Кофейня')
    table_number = models.PositiveIntegerField(verbose_name='Номер столика')
    seats = models.PositiveIntegerField(verbose_name='Кількість місць за столиком')
    is_avaible = models.BooleanField(default=True,verbose_name='Доступный')

    def __str__(self) -> str:
        return f"Назва кофейні:{self.coffeehouse} - Номер столика:{self.table_number} - Кількість місць:{self.seats} - {'Доступный' if self.is_avaible == True else 'Недоступный'}"