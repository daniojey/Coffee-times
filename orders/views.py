from django import forms
from django.forms import widgets
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, View, TemplateView, FormView

from coffeehouses.forms import CreateReservationForm
from coffeehouses.models import CoffeeHouse, Table
from orders.models import Reservation

# Create your views here.

class HomePageOrders(TemplateView):
    template_name = 'orders/index.html'

class CreateReservation(FormView):
    template_name = 'orders/reservation.html'
    form_class= CreateReservationForm
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'coffeehouse' in self.request.GET:
            kwargs['initial'] = {'coffeehouse': self.request.GET['coffeehouse']}
        return kwargs
    
def get_available_tables(request):
    if request.method == 'POST':
        coffeehouse_id = request.GET.get('coffeehouse')
        reservation_date = request.GET.get('reservation_date')
        reservation_time = request.GET.get('reservation_time')
        table_capacity = request.GET.get('table_capacity')
        booking_duration = request.GET.get('booking_duration')

        print(coffeehouse_id)
        print(reservation_date)
        print(reservation_time)
        print(table_capacity)
        print(booking_duration)

        coffeehouse = get_object_or_404(CoffeeHouse, id=coffeehouse_id)

        avaible_tables = Table.objects.filter(coffeehouse=coffeehouse)


        data = [{"id": table.id, 'name': table.table_number} for table in avaible_tables]
        return JsonResponse({'tables': data})
    else:
        return JsonResponse({'tables': 'Нет доступных столиков, выберете пожалуйста другой вариант'})