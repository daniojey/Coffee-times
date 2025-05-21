import json
import re
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, View, TemplateView
from django.contrib.postgres.search import SearchVector

from coffeehouses.models import Category, CoffeeHouse, Product
from orders.models import Reservation
from users.utils import get_actual_reservations

# Create your views here.
class HomePageView(TemplateView):
    template_name ='coffeehouses/indextest.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        products = Product.objects.only('name', 'description', 'image', 'price')[:4]

        context.update({
            'active_tab': 'main-link',
            'products': products,
        })

        return context


class MapCoffeehousesView(TemplateView):
    template_name = 'coffeehouses/map_coffeehouses.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        coffee_shops = CoffeeHouse.objects.all()
        coffee_shops_data = [
            {
                'id': shop.id,
                'image': shop.image.url if shop.image else None,
                'name': shop.name,
                'location': shop.location,
                'address': shop.address,
                'opening_time': shop.opening_time,
                'closing_time': shop.closing_time,
            }
            for shop in coffee_shops
        ]

        context.update({
            'coffee_shops': json.dumps(coffee_shops_data, cls=DjangoJSONEncoder),
            'coffeehouses': coffee_shops,
            'active_tab': 'map-link',
        })

        return context
    
class MenuPageView(ListView):
    template_name = 'coffeehouses/test_menu_page.html'
    context_object_name = 'products'
    paginate_by = 4

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('category', '')

        products = Product.objects.all()

        if category_filter:
            category = Category.objects.filter(name=category_filter).first()

            if category:
                products = products.filter(category=category)
            else:
                products = products.none()

        if search:
            products = products.annotate(
                search=SearchVector("name", "description"),
                ).filter(search=search)
            
            # products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))


        return products


    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page', 1)
        pagination = Paginator(self.get_queryset(), self.paginate_by)

        context = super().get_context_data(**kwargs)
        
        context['page_obj'] = pagination.get_page(page)
        context.update({
            'active_tab': 'menu-link',
        })

        return context
    
    
class ProductView(View):
    
    def get(self, request, *args, **kwargs):
        product_pk = kwargs.get('pk')

        product = get_object_or_404(Product, pk=product_pk)
        context = {
            'product': product,
            'active_tab': 'menu-link',
        }

        return render(request, 'coffeehouses/product.html', context)
    
    
class ReservationSearchView(View):
    template_name = 'coffeehouses/test_search_number_page.html'
    
    def get(self, request, *args, **kwargs):
        # Просто отображаем страницу поиска, если запрос GET
        return render(request, self.template_name, {'active_tab': 'reservation-link'})
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
           return JsonResponse({'reservations': []})
        
        phone = data.get('phone')
        actual = data.get('actual')

        if not phone:
            return JsonResponse({'error': 'По цьому номеру телефону немає бронювань'}, status=400)
        else:
            if phone[0] == '0':
                phone = '38' + phone

            pattern = r'^(?:380|0)\d{9}$'
            if not re.match(pattern, phone):
                return JsonResponse({'error': 'Невірний формат номеру телефону, перевірте  формат введеного номеру'}, status=400)

        if actual:
            reservations = get_actual_reservations(phone)

            # Преобразуем данные бронирований в нужный формат
            reservations_data = [{
                'table_number': item.table.table_number,
                'seats': item.table.seats,
                'date': item.reservation_date,
                'time': str(item.reservation_time),
                'times': str(item.booking_duration).replace("P0DT", "").replace("H", " ч. ").replace("M", " хв.").replace("S", ""),
            } for item in reservations]

            return JsonResponse({'reservations': reservations_data})

        else:
            # Ищем бронирования по номеру телефона
            reservations = Reservation.objects.filter(customer_phone=phone).select_related('coffeehouse', 'table').order_by('-reservation_date')[:20]

            # Преобразуем данные бронирований в нужный формат
            reservations_data = [{
                'table_number': item.table.table_number,
                'seats': item.table.seats,
                'date': item.reservation_date,
                'time': str(item.reservation_time),
                'times': str(item.booking_duration).replace("P0DT", "").replace("H", " ч. ").replace("M", " хв.").replace("S", ""),
            } for item in reservations]

            return JsonResponse({'reservations': reservations_data})