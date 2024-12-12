import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView

from coffeehouses.models import CoffeeHouse, Product
from orders.models import Reservation

# Create your views here.
class HomePageView(TemplateView):
    template_name ='coffeehouses/index.html'


class MapCoffeehousesView(TemplateView):
    template_name = 'coffeehouses/map_coffeehouses.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        coffee_shops = CoffeeHouse.objects.all()
        coffee_shops_data = [
            {
                'id': shop.id,
                'name': shop.name,
                'location': shop.location,
                'address': shop.address,
                'opening_time': shop.opening_time,
                'closed_time': shop.closing_time,
            }
            for shop in coffee_shops
        ]

        context.update({
            'coffee_shops': json.dumps(coffee_shops_data, cls=DjangoJSONEncoder),
        })

        return context
    
class MenuPageView(TemplateView):
    template_name = 'coffeehouses/menu_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'products': Product.objects.all()
        })

        return context
    
class ReservationSearchView(View):
    template_name = 'coffeehouses/search_number_page.html'
    
    def get(self, request, *args, **kwargs):
        # Просто отображаем страницу поиска, если запрос GET
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        # Обрабатываем запрос POST, получаем номер телефона
        data = json.loads(request.body)
        phone = data.get('phone')

        print(phone)
        if phone[0] == '0':
            phone = '38' + phone
        print(phone)

        if not phone:
            return JsonResponse({'error': 'По цьому номеру телефону немає бронювань'}, status=400)

        # Ищем бронирования по номеру телефона
        reservations = Reservation.objects.filter(customer_phone=phone).select_related('coffeehouse', 'table')

        # Преобразуем данные бронирований в нужный формат
        reservations_data = [{
            'table_number': item.table.table_number,
            'seats': item.table.seats,
            'date': item.reservation_date,
            'time': str(item.reservation_time),
            'times': str(item.booking_duration).replace("P0DT", "").replace("H", " ч. ").replace("M", " хв.").replace("S", ""),
        } for item in reservations]

        return JsonResponse({'reservations': reservations_data})