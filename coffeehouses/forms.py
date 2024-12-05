from django import forms
from django.forms import widgets

from coffeehouses.models import Table
from orders.models import Reservation


class CreateReservationForm(forms.ModelForm):
    reservation_date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'reservation_date'})
    )
    reservation_time = forms.TimeField(
        label='Час бронювання',
        widget=forms.TimeInput(attrs={'type': 'time', 'placeholder': 'Години:хвилини (наприклад, 14:30)', 'id': 'reservation_time'})
    )
    booking_duration = forms.TimeField(
        label='Продовжуваність бронювання',
        widget=forms.TimeInput(attrs={'type': 'time', 'id': 'booking_duration'})
    )

    class Meta:
        model = Reservation
        fields = [
            'coffeehouse',
            'customer_name',
            'customer_phone',
            'reservation_date',
            'reservation_time',
            'booking_duration',
            'table',
        ]
        labels = {
            'coffeehouse': "Кав'ярня",
            'customer_name': "Ваше ім'я",
            'customer_phone': 'Номер телефону',
            'reservation_time': 'Час бронювання',
        }
        widgets = {
            'coffeehouse': forms.Select(attrs={'id': 'coffeehouse'}),
            'customer_phone': forms.TextInput(attrs={'type': 'text', 'placeholder': '380xxxxxxxxx', 'id': 'customer_phone'}),
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'id': 'reservation_date'}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time', 'id': 'reservation_time'}),
            'booking_duration': forms.TimeInput(attrs={'type': 'time', 'id': 'booking_duration'}),
            'table': forms.Select(attrs={'id': 'available_tables'})
        }

