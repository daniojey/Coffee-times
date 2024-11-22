from django.contrib import admin
from django.urls import path

from . import views

app_name = 'coffeehouses'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index')
]