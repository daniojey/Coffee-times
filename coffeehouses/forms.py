from datetime import time, timedelta
from django import forms
from django.forms import widgets

from coffeehouses.models import CoffeeHouse, Table
from orders.models import Reservation


class CreateReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            self.fields['customer_name'].required = False
            self.fields['customer_phone'].required = False
            self.fields['customer_name'].widget = forms.HiddenInput()
            self.fields['customer_phone'].widget = forms.HiddenInput()


    reservation_date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'reservation_date', 'class': 'date-input', 'placeholder': 'Оберіть дату'})
    )
    reservation_time = forms.TimeField(
        label='Час бронювання',
        widget=forms.TimeInput(attrs={'type': 'time', 'placeholder': 'Години:хвилини (наприклад, 14:30)', 'id': 'reservation_time', 'class': 'time-input'})
    )
    booking_duration = forms.TimeField(
        label='Продовжуваність бронювання',
        widget=forms.TimeInput(attrs={'type': 'time', 'id': 'booking_duration', 'class': 'time-input'})
    )


    class Meta:
        model = Reservation
        fields = [
            'customer_name',
            'customer_phone',
            'coffeehouse',
            'reservation_date',
            'reservation_time',
            'booking_duration',
            'table',
        ]
        labels = {
            'coffeehouse': "Кав'ярня",
            'customer_phone': 'Номер телефону',
            'reservation_time': 'Час бронювання',
            'table': 'Оберіть столик'
        }
        widgets = {
            'coffeehouse': forms.Select(attrs={'id': 'coffeehouse', 'class': 'custom-select'}),
            'customer_name': forms.TextInput(attrs={'type': 'text', 'placeholder': "Введіть ім'я", 'id': 'customer_phone', 'class':'custom-input'}),
            'customer_phone': forms.TextInput(attrs={'type': 'text', 'placeholder': '380xxxxxxxxx', 'id': 'customer_phone', 'class':'custom-input'}),
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'id': 'reservation_date', 'class': 'date-input','placeholder': 'Оберіть дату'}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time', 'id': 'reservation_time', 'class': 'time-input'}),
            'booking_duration': forms.TimeInput(attrs={'type': 'time', 'id': 'booking_duration', 'class': 'time-input'}),
            'table': forms.Select(attrs={'id': 'available_tables', 'class': 'custom-table'})
        }
    
    def clean_booking_duration(self):
        duration = self.cleaned_data.get('booking_duration')
        print(duration, type(duration))
        if isinstance(duration, time):
            # Преобразуем в timedelta
            duration = timedelta(hours=duration.hour, minutes=duration.minute)
        elif isinstance(duration, str):
            # Если это строка, пытаемся распарсить
            try:
                hours, minutes = map(int, duration.split(':'))
                duration = timedelta(hours=hours, minutes=minutes)
            except ValueError:
                raise forms.ValidationError("Invalid duration format. Use HH:MM.")
        return duration
