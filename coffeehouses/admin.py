from django.contrib import admin

from coffeehouses.models import CoffeeHouse, Table

# Register your models here.

admin.site.register(CoffeeHouse)
admin.site.register(Table)