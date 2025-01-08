from django.contrib import admin

from coffeehouses.models import Category, CoffeeHouse, Product, Table
from unfold.admin import ModelAdmin

# Register your models here.


@admin.register(Category)
class CategoriesAdmin(ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name",]


@admin.register(Product)
class ProductClass(ModelAdmin):
    pass

@admin.register(CoffeeHouse)
class CoffeehouseClass(ModelAdmin):
    pass

@admin.register(Table)
class TableClass(ModelAdmin):
    pass
# admin.site.register(Product)
# admin.site.register(CoffeeHouse)
# admin.site.register(Table)