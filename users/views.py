import re
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from users.forms import UserLoginForm, UserRegistrationForm
from users.models import User

class LoginView(FormView):
    template_name='users/login.html'
    form_class=UserLoginForm
    success_url=reverse_lazy('coffeehouses:index')

    def form_valid(self, form) -> HttpResponse:
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(self.request, username=username, password=password)
        if user:
            self.object = user
            login(self.request, user=user)

            return super().form_valid(form) 
        else:
            form.add_error(None, "Невірний логин або номер телефону або пароль")
            return self.form_invalid(form)


class RegistrationView(FormView):
    template_name='users/registration.html'
    form_class=UserRegistrationForm
    success_url=reverse_lazy('coffeehouses:index')

    def form_valid(self, form) -> HttpResponse:
        user = form.save(commit=False)
        phone = form.cleaned_data.get('phone', None)

        pattern = r'^(?:380|0)\d{9}$'
        if re.match(pattern, phone):
            if phone[0] == '0':
                phone = '38' + phone
            if User.objects.filter(phone=phone).exists():
                form.add_error('phone', 'Такий номер телефону вже існує')
                return self.form_invalid(form)
        else:
            form.add_error('phone', 'Неверный формат номера телефона. Укажите номер в формате 380123456789 или 0123456789.')
            return self.form_invalid(form)


        user.phone = phone
        user.save()  # Сохраняем пользователя в базе данных
        
        self.object = user
        login(self.request, user=user)
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    


def profile(request):
    return redirect(reverse("coffeehouses:index"))

def logout(request):
    auth.logout(request)
    return redirect(reverse("coffeehouses:index"))