from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, View, TemplateView, FormView
from django.db.models import F, Q, DurationField, ExpressionWrapper, TimeField

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
            booking_duration = data.get('booking_duration')

            # # Конвертируем строковые данные в datetime
            # start_time_str = f"{reservation_date} {reservation_time}"
            # start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")

            # # Обработка длительности бронирования
            # try:
            #     duration_parts = booking_duration.split(":")
            #     hours = int(duration_parts[0])
            #     minutes = int(duration_parts[1])
            #     duration = timedelta(hours=hours, minutes=minutes)
            # except (IndexError, ValueError):
            #     return JsonResponse({'error': 'Invalid booking_duration format. Expected "HH:MM".'}, status=400)

            # end_time = start_time + duration

            # # 1. Рассчитываем start_datetime и end_datetime для всех бронирований с учётом даты и времени
            # reservations_with_end_time = Reservation.objects.annotate(
            #     start_datetime=ExpressionWrapper(
            #         F('reservation_date') + F('reservation_time'),
            #         output_field=DateTimeField()
            #     ),
            #     end_datetime=ExpressionWrapper(
            #         F('reservation_date') + F('reservation_time') + F('booking_duration'),
            #         output_field=DateTimeField()
            #     )
            # )

            # # 2. Фильтруем бронирования с пересечением времени
            # overlapping_reservations = reservations_with_end_time.filter(
            #     table__coffeehouse_id=coffeehouse_id,  # Учитываем кофейню
            #     reservation_date=reservation_date,
            #     # Бронирование должно пересекаться с новым, то есть:
            #     #  - начнется до окончания нового бронирования
            #     #  - или закончится после начала нового бронирования
            #     start_datetime__lt=end_time,        # Бронирование начинается до окончания нового
            #     end_datetime__gt=start_time         # Бронирование заканчивается после начала нового
            # )

            # # 3. Находим ID занятых столиков
            # reserved_tables = overlapping_reservations.values_list('table_id', flat=True)

            # # 4. Получаем доступные столики
            # available_tables = Table.objects.filter(coffeehouse_id=coffeehouse_id).exclude(id__in=reserved_tables)

            reservations_today = Reservation.objects.filter(coffeehouse_id=coffeehouse_id ,reservation_date=reservation_date)
            print(reservations_today)
            for item in reservations_today:
                print(item.table)

            annotations_reservation = reservations_today.annotate(
                end_time=ExpressionWrapper(
                    F('reservation_time') + F('booking_duration'),
                    output_field=TimeField()
                )
            )
 
            for reservation in annotations_reservation:
                print(reservation.end_time)

             # Фильтруем пересекающиеся брони
            overlapping_reservations = annotations_reservation.filter(end_time__lt=reservation_time)
            print(reservation_time)

            print(overlapping_reservations)


            # Формируем данные для ответа
            tables_data = [{"id": table.id, 'name': table.table_number} for table in Table.objects.all()]
            return JsonResponse({'tables': tables_data})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    else:
        return JsonResponse({'tables': 'Нет доступных столиков, выберете пожалуйста другой вариант'}, status=405)