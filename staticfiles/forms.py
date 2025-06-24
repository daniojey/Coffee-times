from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import User

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'phone',
            'password1',
            'password2',
        )

    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логін', "id": "username"}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефону', "id": "phone"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль', "id": "password1"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторіть пароль', "id": "password2"}))     