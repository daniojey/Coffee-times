from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, verbose_name='номер телефону')
    
    def __str__(self):
        return  f"{self.username} - {self.phone}"

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"