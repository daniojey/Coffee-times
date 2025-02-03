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
    list_select_related = True
    list_display = ["name", "category", "price", "discount"]
    list_editable = ["price", "discount"]
    search_fields = ["name", "category__name"]

@admin.register(CoffeeHouse)
class CoffeehouseClass(ModelAdmin):
    list_display = ["name", "address", "opening_time", "closing_time"]
    search_fields = ["name", "address", "opening_time", "closing_time"]


@admin.display(description="coffeehouse_name")
def coffeehouse_name(obj):
    return f"{obj.coffeehouse.name}"
@admin.register(Table)


class TableClass(ModelAdmin):
    list_select_related = True
    list_display =  [coffeehouse_name, "table_number", "seats"]
    search_fields = ["coffeehouse__name", "table_number"]


# admin.site.register(Product)
# admin.site.register(CoffeeHouse)
# admin.site.register(Table)