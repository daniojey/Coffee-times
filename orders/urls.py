from django.contrib import admin
from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.HomePageOrders.as_view(), name='index'),
    path('reservation/', views.CreateReservation.as_view(), name='reservation'),
    path('reservation/get_tables/', views.get_available_tables, name='get_tables'),
    path('reservation/get-available-times/', views.get_available_times, name='get-available-times'),
    path('reservation/get-booking-duration/', views.get_booking_duration, name='get_booking_duration'),
]