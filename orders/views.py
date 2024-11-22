from django.shortcuts import render
from django.views.generic import View, TemplateView

# Create your views here.

class HomePageOrders(TemplateView):
    template_name = 'orders/index.html'