from datetime import datetime, timedelta, time
import json
import re
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, TemplateView, FormView
from django.db.models import F, Q, ExpressionWrapper, TimeField

from coffeehouses.forms import CreateReservationForm
from coffeehouses.models import CoffeeHouse, Table
from orders.models import Reservation
from django.views.decorators.csrf import csrf_exempt

from users.utils import get_actual_reservations, get_user_ip

# Create your views here.

class HomePageOrders(TemplateView):
    template_name = 'orders/index.html'

class CreateReservation(FormView):
    template_name = 'orders/reservation.html'
    form_class= CreateReservationForm
    success_url = reverse_lazy('coffeehouses:index')

    def form_valid(self, form):
        user = self.request.user
        ip = get_user_ip(self.request)
        # print(self.request.POST)

        # actual_reservations = get_actual_reservations(phone=user.phone)
        # if len(actual_reservations) >= 2:
        #     return JsonResponse({'status': 'success', 'message': 'Вы создали слишком много резерваций, вы сможете создать новую если отмените одну из созданных ранее.'})
        
        # reservation_ip = get_actual_reservations(ip=ip)
        # if len(reservation_ip) >= 2:
        #     return JsonResponse({'status': 'success', 'message': 'Вы создали слишком много резерваций, вы сможете создать новую если отмените одну из созданных ранее.'})

        reservation_time = self.request.POST['reservation_time']
        booking_duration = self.request.POST['booking_duration']
        table = self.request.POST["table"]
        reservation_date = self.request.POST['reservation_date']
        coffeehouse_id = self.request.session.get('coffeehouse')

        # Преобразуем reservation_time в объект времени
        reservation_time_obj = datetime.strptime(reservation_time, "%H:%M").time()

        # Преобразуем строки в часы и минуты
        h2, m2 = map(int, booking_duration.split(':'))
        reservation_datetime = datetime.combine(datetime.strptime(reservation_date, "%Y-%m-%d"), reservation_time_obj)

        # Создаём объект timedelta и объект datetime
        delta2 = timedelta(hours=h2, minutes=m2)

        # Складываем время
        total_time = reservation_datetime + delta2

        end_time = total_time.time()

        reservation_filter = Reservation.objects.filter(coffeehouse__id=coffeehouse_id, table__table_number=table, reservation_date=reservation_date).select_related("table")
        reservations_exists = reservation_filter.annotate(
            end_time = ExpressionWrapper(
                    F('reservation_time') + F('booking_duration'),
                    output_field=TimeField()
                )
        )

        result = reservations_exists.filter(Q(end_time__gt=reservation_time) & Q(reservation_time__lt=end_time))

        if result:
            return ValidationError("Помилка: бронювання на данный час і столик вже створене, оберіть будь-ласка інший час або столик")

        if user.is_authenticated:
            reservation = form.save(commit=False)
            reservation.customer_name = user.username
            reservation.customer_phone = user.phone
            reservation.created_ip = ip
            reservation.save()
        else:
            reservation = form.save(commit=False)
            reservation.created_ip = ip
            reservation.save()

        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        kwargs['user'] = user
        
        coffeehouse_id = self.request.GET.get('coffeehouse', None)
        
        if coffeehouse_id:
            try:
                # Ищем кофейню по id
                coffeehouse = CoffeeHouse.objects.get(id=coffeehouse_id)
                # Передаем кофейню в initial
                kwargs['initial'] = kwargs.get('initial', {})
                kwargs['initial']['coffeehouse'] = coffeehouse
            except CoffeeHouse.DoesNotExist:
                pass  # Можно обработать исключение, если кофейня не найдена
        return kwargs
    


@csrf_exempt
def get_available_tables(request):
    ip = get_user_ip(request=request)
    if request.method == 'POST':
        try:
            # Парсим данные из тела запроса
            data = json.loads(request.body)
            coffeehouse_id = data.get('coffeehouse')
            reservation_date = data.get('reservation_date')
            reservation_time = data.get('reservation_time')
            booking_duration = data.get('booking_duration')

            reservations_today = Reservation.objects.filter(coffeehouse_id=coffeehouse_id ,reservation_date=reservation_date).select_related('table')
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


            # Преобразуем reservation_time в объект времени
            reservation_time_obj = datetime.strptime(reservation_time, "%H:%M").time()

            # Преобразуем booking_duration в timedelta
            hours, minutes = map(int, booking_duration.split(":"))
            booking_duration_td = timedelta(hours=hours, minutes=minutes)

            # Объединяем reservation_date и reservation_time для получения datetime
            reservation_datetime = datetime.combine(datetime.strptime(reservation_date, "%Y-%m-%d"), reservation_time_obj)

            # Добавляем продолжительность
            end_datetime = reservation_datetime + booking_duration_td

            # Извлекаем только время окончания
            end_time = end_datetime.time()

             # Фильтруем пересекающиеся брони
            overlapping_reservations = annotations_reservation.filter(end_time__gt=reservation_time).filter(reservation_time__lt=end_time).values_list('table_id', flat=True)


            # Формируем данные для ответа
            tables_data = [{"id": table.id, 'name': table.table_number} for table in Table.objects.filter(coffeehouse_id=coffeehouse_id).exclude(id__in=overlapping_reservations)]
            request.session['coffeehouse'] = coffeehouse_id
            return JsonResponse({'tables': tables_data})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    else:
        return JsonResponse({'tables': 'Нет доступных столиков, выберете пожалуйста другой вариант'}, status=405)
    


def get_available_times(request):
    date_str = request.GET.get('date')
    coffeehouse_id = request.GET.get('coffeehouse', None)
    if coffeehouse_id or coffeehouse_id != '':
        coffeehouse = CoffeeHouse.objects.get(id=coffeehouse_id)
    else:
        coffeehouse = None

    now = datetime.now()

    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        selected_date = now

    time_choices = []
    start_hour = now.hour if selected_date.date() == now.date() else 0
    start_minute = now.minute if selected_date.date() == now.date() else 0
    end_hour = 24

    if coffeehouse:
        # Если сегодняшняя дата и время сейчас меньше чем время открытия кафе
        if now.time() < coffeehouse.opening_time and selected_date.date() == now.date():
            st_hour = coffeehouse.opening_time
            en_hour = coffeehouse.closing_time

            start_hour = str(st_hour).split(':')
            end_hour = str(en_hour).split(':')

            start_hour = int(start_hour[0])
            end_hour = int(end_hour[0])

        # Если дата сегодняшняя но время у при котором пользователь зашёл создать резервацию позже чем открытие кофейни
        # то высталяем лишь ограничение на закрытие
        elif now.time() > coffeehouse.opening_time and selected_date.date() == now.date():
            en_hour = coffeehouse.closing_time
            end_hour = str(en_hour).split(':')
            end_hour = int(end_hour[0]) 

        # Если другая дата то ограничиваем время лишь по открытию и закрытию
        elif selected_date.date() != now.date():
            st_hour = coffeehouse.opening_time
            en_hour = coffeehouse.closing_time

            start_hour = str(st_hour).split(':')
            end_hour = str(en_hour).split(':')

            start_hour = int(start_hour[0])
            end_hour = int(end_hour[0])
        
        
    for hour in range(start_hour, end_hour):
        for minute in range(0, 60, 30):
            if hour > start_hour or (hour == start_hour and minute >= start_minute):
                time_str = f"{hour:02}:{minute:02}"
                time_choices.append(time_str)
                
    if len(time_choices) == 0:
        return JsonResponse({'times': [], 'message': 'Нет доступного времени на сегодня'})
    else:
        time_choices.pop()
        return JsonResponse({'times': time_choices})
    


def get_booking_duration(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            coffeehouse_id = data.get('coffeehouse')
            reservation_time = data.get('reservation_time')

            coffeehouse = get_object_or_404(CoffeeHouse, id=coffeehouse_id)

            # Преобразуем время закрытия и время бронирования в datetime
            closing_time = datetime.strptime(coffeehouse.closing_time.strftime("%H:%M"), "%H:%M")
            reservation_time = datetime.strptime(reservation_time, "%H:%M")

            # Вычисляем разницу между временем закрытия и временем бронирования
            difference = closing_time - reservation_time

            if difference.total_seconds() <= 0:
                # Если разница отрицательная или равна 0, бронирование невозможно
                return JsonResponse({'data': ["00:00"]})

            # Получаем оставшиеся часы и минуты
            remaining_hours, remainder = divmod(difference.seconds, 3600)
            remaining_minutes = remainder // 60

            durations = []

            # Генерация доступных интервалов времени
            if remaining_hours <= 3:
                for hour in range(remaining_hours + 1):
                    for minute in range(0, 60, 15):  # Интервалы по 15 минут
                        if hour == remaining_hours and minute > remaining_minutes:
                            break  # Прерываем, если минуты выходят за пределы оставшегося времени
                        elif hour > 4 and minute > remaining_minutes:
                            break

                        durations.append(f"{hour:02}:{minute:02}")
            else:
                for hour in range(4):
                    for minute in range(0, 60, 15):  # Интервалы по 15 минут
                        if hour == 3 and minute > 0:
                            break
                        durations.append(f"{hour:02}:{minute:02}")

            if len(durations) == 0:
                durations.append("00:00")

            return JsonResponse({'data': durations})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Ошибка логики'}, status=405)


