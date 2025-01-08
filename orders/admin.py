from django.contrib import admin

from orders.models import Reservation
from unfold.admin import ModelAdmin

@admin.register(Reservation)
class ReservationClass(ModelAdmin):
    pass
# admin.site.register(Reservation)