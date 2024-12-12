from django.contrib import admin

from coffeehouses.models import Category, CoffeeHouse, Product, Table

# Register your models here.


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name",]

admin.site.register(Product)
admin.site.register(CoffeeHouse)
admin.site.register(Table)