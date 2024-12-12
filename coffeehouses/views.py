import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import View, TemplateView

from coffeehouses.models import CoffeeHouse, Product

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
    