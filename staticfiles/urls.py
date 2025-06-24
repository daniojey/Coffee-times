from django.urls import path


from . import views

app_name = 'users'

urlpatterns = [
    path('oauth/login/', views.google_login, name='google_login'),
    path('oauth/callback/', views.google_callback, name='google_callback'),
    path('oauth/get-phone/', views.get_phone, name='get_phone'),
    path('login/', views.LoginView.as_view() , name='login'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('history/', views.HistoryReservationView.as_view(), name='reservation_history'),
    path('delete-reservation/<int:pk>/', views.DeleteReservationView.as_view(), name='delete_reservation'),
    path('logout/', views.logout, name='logout'),
]

