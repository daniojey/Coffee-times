from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, TemplateView, FormView
from django.db.models import F, ExpressionWrapper, TimeField

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

        actual_reservations = get_actual_reservations(phone=user.phone)
        if len(actual_reservations) >= 2:
            return JsonResponse({'status': 'success', 'message': 'Вы создали слишком много резерваций, вы сможете создать новую если отмените одну из созданных ранее.'})
        
        reservation_ip = get_actual_reservations(ip=ip)
        if len(reservation_ip) >= 2:
            return JsonResponse({'status': 'success', 'message': 'Вы создали слишком много резерваций, вы сможете создать новую если отмените одну из созданных ранее.'})

        if user.is_authenticated:
            reservation = form.save(commit=False)
            reservation.customer_name = user.username
            reservation.customer_phone = user.phone
            reservation.ip = ip
            reservation.save()
        else:
            reservation = form.save(commit=False)
            reservation.ip = ip
            reservation.save()

        return super().form_valid(form)
    

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
    print(ip)
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

            print(end_datetime)
            print(end_time)


             # Фильтруем пересекающиеся брони
            overlapping_reservations = annotations_reservation.filter(end_time__gt=reservation_time).filter(reservation_time__lt=end_time).values_list('table_id', flat=True)


            # Формируем данные для ответа
            tables_data = [{"id": table.id, 'name': table.table_number} for table in Table.objects.filter(coffeehouse_id=coffeehouse_id).exclude(id__in=overlapping_reservations)]
            return JsonResponse({'tables': tables_data})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    else:
        return JsonResponse({'tables': 'Нет доступных столиков, выберете пожалуйста другой вариант'}, status=405)