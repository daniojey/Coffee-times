from django.urls import path


from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view() , name='login'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('history/', views.HistoryReservationView.as_view(), name='reservation_history'),
    path('logout/', views.logout, name='logout'),
    
]

