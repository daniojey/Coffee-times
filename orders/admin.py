from django.contrib import admin

from orders.models import Reservation
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import FieldTextFilter

@admin.register(Reservation)
class ReservationClass(ModelAdmin):
    list_filter_submit = True
    list_filter = [
        ("customer_phone", FieldTextFilter),
        ("customer_name", FieldTextFilter),
        
    ]
# admin.site.register(Reservation)