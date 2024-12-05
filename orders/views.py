from django import forms
from django.forms import widgets
from django.shortcuts import render
from django.views.generic import CreateView, View, TemplateView, FormView

from coffeehouses.forms import CreateReservationForm
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