from django import forms
from django.forms import widgets

from coffeehouses.models import Table
from orders.models import Reservation


class CreateReservationForm(forms.ModelForm):
    reservation_date = forms.DateField(label='Data', widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Reservation
        fields= [ 
            'coffeehouse',
            'table',
            'customer_name',
            'customer_phone',
            'reservation_date',
            'reservation_time',]
        
        labels = {
            'coffeehouse': "Кав'ярня",
            'customer_name': "Ваше ім'я",
            'customer_phone': 'Номер телефону',
            'reservation_time': 'Час бронювання години|хвилини',
        }
        
        widgets= {
            'customer_phone': forms.TextInput(attrs={'type': 'text', 'placeholder': '380xxxxxxxxx'}),
            'reservation_date' : forms.DateInput(attrs={'type': 'date', 'label':'Дата'}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time', 'placeholder': 'Часы:Минуты (например, 14:30)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтрация столиков по выбранной кофейне
        if 'coffeehouse' in self.initial:
            self.fields['table'].queryset = Table.objects.filter(coffeehouse=self.initial['coffeehouse'])

