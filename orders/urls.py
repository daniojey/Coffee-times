from django.contrib import admin
from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.HomePageOrders.as_view(), name='index'),
    path('reservation/', views.CreateReservation.as_view(), name='reservation'),
]