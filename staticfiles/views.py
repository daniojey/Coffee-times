import re
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

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

        print(s_sort_by)

        user = self.request.user
        if user.phone:
            reservations = Reservation.objects.filter(customer_phone=user.phone)
        else:
            reservations = Reservation.objects.filter(customer_name=user.username)

        if s_active:
            if user.phone:
                reservations = get_actual_reservations(phone=user.phone)
            else:
                reservations = get_actual_reservations(username=user.username)

        if s_coffeehouse:
            reservations = reservations.order_by('coffeehouse')
        

        if s_sort_by:
            if s_sort_by == 'date':
                print('1')
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

def logout(request):
    auth.logout(request)
    return redirect(reverse("coffeehouses:index"))