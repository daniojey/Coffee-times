from django.urls import path
from django.contrib.auth import views as auth_views



from . import views

app_name = 'api'

urlpatterns = [
    path("login/", views.LoginViewApi.as_view() , name="login"),
    path('csrf_token/', views.get_csrf_token, name='csrf_token'),
    path("check_user/", views.CheckAuthUserViewApi.as_view() , name="check_user"),
    path("logout/", views.UserLogoutViewApi.as_view() , name="logout"),
    path("product_categories/", views.ProductCategoryAPI.as_view() , name="product_categories"),
    path("create_products/", views.ProductCreateViewAPI.as_view() , name="create_products"),
    path("reservations_search/", views.ReservationSearchAPI.as_view(), name="reservation_search"),
    path("user_profile/", views.ProfileInfoAPI.as_view(), name="user_profile"),
    path("user_history_reservations/", views.ProfileHitoryAPI.as_view(), name="user_history_reservations"),
    path("create_reservation/", views.CreateReservationAPI.as_view(), name="create_reservation"),
]
