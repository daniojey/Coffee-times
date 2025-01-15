import re
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, FormView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from decouple import config
import requests

from orders.models import Reservation
from users.forms import UserLoginForm, UserRegistrationForm
from users.models import User
from users.utils import get_actual_reservations, get_user_ip

class LoginView(FormView):
    template_name='users/login.html'
    form_class=UserLoginForm
    success_url=reverse_lazy('coffeehouses:index')

    def form_valid(self, form) -> HttpResponse:
        _next =  self.request.GET.get('next')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(self.request, username=username, password=password)
        if user:
            self.object = user
            login(self.request, user=user)

            if _next:
                return HttpResponseRedirect(_next)
            
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
    


class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = 'users/profile.html'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        
        if not user.phone:
            actual_reservations = get_actual_reservations(username=user.username)
        else:
            actual_reservations = get_actual_reservations(phone=user.phone)

        
        actual_res_list = actual_reservations.values_list('id', flat=True)[:2]
        reservations = Reservation.objects.filter(customer_name=user.username, customer_phone=user.phone).exclude(id__in=actual_res_list).order_by('-reservation_date')[:3]

        context.update({
            'user': user,
            'actual_reservations': actual_reservations,
            'reservations': reservations
        })

        return context

class HistoryReservationView(LoginRequiredMixin, ListView):
    redirect_field_name = 'next'
    template_name = "users/user_history.html"
    context_object_name = 'reservations'
    paginate_by = 5

    def get_queryset(self):
        s_active = self.request.GET.get('is_active', '')
        s_coffeehouse = self.request.GET.get('is_cafe', '')
        s_sort_by = self.request.GET.get('sort_by', '')

        user = self.request.user
        if user.phone:
            reservations = Reservation.objects.filter(customer_phone=user.phone).select_related('coffeehouse')
        else:
            reservations = Reservation.objects.filter(customer_name=user.username).select_related('coffeehouse')

        if s_active:
            if user.phone:
                reservations = get_actual_reservations(phone=user.phone)
            else:
                reservations = get_actual_reservations(username=user.username)

        if s_coffeehouse:
            reservations = reservations.order_by('coffeehouse')
        

        if s_sort_by:
            if s_sort_by == 'date':
                reservations = reservations.order_by('-reservation_date')
            elif s_sort_by == 'time':
                reservations = reservations.order_by('reservation_time')


        return reservations

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        
        page = self.request.GET.get('page', 1)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        context['page_obj'] = paginator.get_page(page)

        context['filter'] = self.request.GET.get('filter', '')

        return context

class DeleteReservationView(DeleteView):
    model = Reservation
    success_url = reverse_lazy('users:profile')

def logout(request):
    auth.logout(request)
    return redirect(reverse("coffeehouses:index"))


# Константы Google OAuth
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URL')
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'


def google_login(request):
    # URL для запроса авторизации
    auth_url = (
        f"{GOOGLE_AUTH_URL}?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&scope=email profile"
    )
    return redirect(auth_url)



def google_callback(request):
    # Получение кода из запроса
    code = request.GET.get('code')
    if not code:
        return render(request, 'error.html', {'message': 'Authorization failed'})

    # Обмен кода на токен
    token_data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')

    # Получение информации о пользователе
    user_info_response = requests.get(
        GOOGLE_USER_INFO_URL,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_info = user_info_response.json()

    # Извлечение данных о пользователе
    email = user_info.get('email')
    first_name = user_info.get('given_name', 'User')
    last_name = user_info.get('family_name', '')

    # Проверяем, есть ли пользователь с таким email
    user = User.objects.filter(email=email).first()

    if user:
        # Если пользователь уже существует, входим
        login(request, user)
        return redirect('coffeehouses:index')  # Перенаправление на главную страницу
    else:
        # Если пользователя нет, создаём нового
        username = email.split('@')[0]  # Генерация username на основе email
        phone = request.session.get('phone')  # Проверяем, есть ли телефон в сессии

        if not phone:
            # Если телефона нет, перенаправляем на страницу для ввода телефона
            request.session['google_user_info'] = {
                'email': email,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            }
            return redirect('users:get_phone')  # URL для ввода телефона

        # Создаём пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=None,  # OAuth пользователи могут не иметь пароля
            phone=phone
        )
        user.save()

        # Входим в систему
        login(request, user)

    return redirect('coffeehouses:index')  # Перенаправление на главную страницу


def get_phone(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        google_user_info = request.session.get('google_user_info')

        pattern = r'^(?:380|0)\d{9}$'
        if re.match(pattern, phone):
            if phone[0] == '0':
                phone = '38' + phone
        else:
            request.session['get_phone_error'] = 'Невірний формат телефону, введіть вірний формат номеру'
            return redirect('users:get_phone')

        if google_user_info and phone:

            if not User.objects.filter(phone=phone).exists():
                # Создаём пользователя с указанным телефоном
                user = User.objects.create_user(
                    username=google_user_info['username'],
                    email=google_user_info['email'],
                    first_name=google_user_info['first_name'],
                    last_name=google_user_info['last_name'],
                    password=None,  # OAuth пользователи могут не иметь пароля
                    phone=phone
                )
                user.save()

                # Входим в систему
                login(request, user)

                del request.session['get_phone_error']
                return redirect('coffeehouses:index')
            else:
                # Если пользователь существует переводим на страничку с логином и очищаем сессию
                del request.session['google_user_info']

                if 'get_phone_error' in request.session:
                    del request.session['get_phone_error']
                return redirect('users:login')
            
    context = {
        'title': 'Створення аккаунту',
        'phone_error': request.session['get_phone_error'] if 'get_phone_error' in request.session else None
    }

    return render(request, 'users/get_phone.html', context=context)