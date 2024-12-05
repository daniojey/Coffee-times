from django.db import models

from coffeehouses.models import CoffeeHouse, Table

# Create your models here.
class Reservation(models.Model):
    coffeehouse = models.ForeignKey(CoffeeHouse, on_delete=models.CASCADE, related_name='reservations', verbose_name='Столик')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='tables')
    customer_name = models.CharField(max_length=255, verbose_name="Ім'я кліета")
    customer_phone = models.CharField(max_length=15, verbose_name="Телефон")
    reservation_date = models.DateField(verbose_name="Дата бронювання")
    reservation_time = models.TimeField(verbose_name="Час бронювання")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заказа")

    def __str__(self) -> str:
        return f"Кав'ярня:{self.coffeehouse} - Ім'я кліента:{self.customer_name} - Номер Телефону:{self.customer_phone} - Дата та час бронювання:{self.reservation_date}|{self.reservation_time}"