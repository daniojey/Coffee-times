from django.urls import path


from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view() , name='login'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    
]

