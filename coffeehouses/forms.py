from datetime import date, time, timedelta
from django import forms
from django.forms import ValidationError, widgets

from orders.models import Reservation
from orders import widgets


class CreateReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            self.fields['customer_name'].required = False
            self.fields['customer_phone'].required = False
            self.fields['customer_name'].widget = forms.HiddenInput()
            self.fields['customer_phone'].widget = forms.HiddenInput()
        
        self.fields['reservation_date'].widget.attrs['min'] = date.today().isoformat()

    reservation_date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'reservation_date', 'class': 'date-input', 'placeholder': 'Оберіть дату'})
    )
    # reservation_time = forms.TimeField(
    #     label='Час бронювання',
    #     widget=forms.TimeInput(attrs={'type': 'time', 'placeholder': 'Години:хвилини (наприклад, 14:30)', 'id': 'reservation_time', 'class': 'time-input'})
    # )
    # booking_duration = forms.TimeField(
    #     label='Продовжуваність бронювання',
    #     widget=forms.TimeInput(attrs={'type': 'time', 'id': 'booking_duration', 'class': 'time-input'})
    # )


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
            'table': 'Оберіть столик',
            'booking_duration': "Продовжуваність",
        }

        widgets = {
            'coffeehouse': forms.Select(attrs={'id': 'coffeehouse', 'class': 'custom-select'}),
            'customer_name': forms.TextInput(attrs={'type': 'text', 'placeholder': "Введіть ім'я", 'id': 'customer_phone', 'class':'custom-input'}),
            'customer_phone': forms.TextInput(attrs={'type': 'text', 'placeholder': '380xxxxxxxxx', 'id': 'customer_phone', 'class':'custom-input'}),
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'id': 'reservation_date', 'class': 'date-input','placeholder': 'Оберіть дату'}),
            'reservation_time': widgets.CustomTimeSelect(attrs={'id': 'reservation_time', 'class': 'time-input'}),
            'booking_duration': widgets.CustomBookingSelect(attrs={'id': 'booking_duration', 'class': 'time-input'}),
            'table': forms.Select(attrs={'id': 'available_tables', 'class': 'custom-table'})
        }
    
    def clean_booking_duration(self):
        duration = self.cleaned_data.get('booking_duration')
        refactor_time = str(duration).split(":")
        res = timedelta(hours=int(refactor_time[1]), minutes=int(refactor_time[2]))
        return res

    def clean_reservation_date(self):
        reservation_date = self.cleaned_data['reservation_date']
        if reservation_date < date.today():
            raise ValidationError("Неможливо обрати дату раніше сьогоднішньої.")
        return reservation_date