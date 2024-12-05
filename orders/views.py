import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, View, TemplateView, FormView

from coffeehouses.forms import CreateReservationForm
from coffeehouses.models import CoffeeHouse, Table
from orders.models import Reservation
from django.views.decorators.csrf import csrf_exempt

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
    


@csrf_exempt
def get_available_tables(request):
    if request.method == 'POST':
        try:
            # Парсим данные из тела запроса
            data = json.loads(request.body)
            coffeehouse_id = data.get('coffeehouse')
            reservation_date = data.get('reservation_date')
            reservation_time = data.get('reservation_time')
            table_capacity = data.get('table_capacity')
            booking_duration = data.get('booking_duration')

            # Логирование полученных данных
            print(coffeehouse_id, reservation_date, reservation_time, table_capacity, booking_duration)

            # Получаем объект кофейни
            coffeehouse = get_object_or_404(CoffeeHouse, id=coffeehouse_id)

            # Получаем доступные столики
            available_tables = Table.objects.filter(coffeehouse=coffeehouse)
            print(available_tables)

            # Формируем данные для ответа
            tables_data = [{"id": table.id, 'name': table.table_number} for table in available_tables]
            return JsonResponse({'tables': tables_data})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    else:
        return JsonResponse({'tables': 'Нет доступных столиков, выберете пожалуйста другой вариант'}, status=405)