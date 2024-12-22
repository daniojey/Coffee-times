import re
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from orders.models import Reservation
from users.forms import UserLoginForm, UserRegistrationForm
from users.models import User
from users.utils import get_actual_reservations

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
    


class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        reservations = Reservation.objects.filter(customer_name=user.username, customer_phone=user.phone).order_by('-reservation_date')[:3]
        actual_reservations = get_actual_reservations(phone=user.phone)
        print(actual_reservations)

        context.update({
            'user': user,
            'actual_reservations': actual_reservations,
            'reservations': reservations
        })

        return context

class HistoryReservationView(LoginRequiredMixin, ListView):
    template_name = "users/user_history.html"
    context_object_name = 'reservations'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        if user.phone:
            reservations = Reservation.objects.filter(customer_phone=user.phone).order_by('-reservation_date')
        else:
            reservations = Reservation.objects.filter(customer_name=user.username)

        # Применение фильтров
        filter_query = self.request.GET.get('filter', '')
        if filter_query:
            reservations.filter(Q(coffeehouse_icontains=filter_query) | Q(reservation_date__icontains=filter_query))

        created_date = self.request.GET.get('date_added', '')
        if created_date:
            reservations.order_by('-reservation_date')

        return reservations

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        
        page = self.request.GET.get('page', 1)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        context['page_obj'] = paginator.get_page(page)

        context['filter'] = self.request.GET.get('filter', '')

        return context

def logout(request):
    auth.logout(request)
    return redirect(reverse("coffeehouses:index"))