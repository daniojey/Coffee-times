from django.contrib import admin
from django.urls import path


from . import views

app_name = 'coffeehouses'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('map/', views.MapCoffeehousesView.as_view(), name='coffee_map'),
    path('menu/', views.MenuPageView.as_view(), name='menu_page'),
]

