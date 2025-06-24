from django.urls import path
from django.contrib.auth import views as auth_views



from . import views

app_name = 'api'

urlpatterns = [
    path("login/", views.LoginViewApi.as_view() , name="login"),
    path("register/", views.RegistrationViewApi.as_view() , name="register"),
    path('csrf_token/', views.get_csrf_token, name='csrf_token'),
    path("check_user/", views.CheckAuthUserViewApi.as_view() , name="check_user"),
    path("logout/", views.UserLogoutViewApi.as_view() , name="logout"),
    path('token-logout/', views.LogoutTokenAPIView.as_view(), name='token-logout'),
    path("product_categories/", views.ProductCategoryAPI.as_view() , name="product_categories"),
    path("products-homepage/", views.ProductHomePageApiView.as_view(), name="products_homepage"),
    path("products-menupage/", views.ProductMenuPageAPI.as_view(), name="products_menupage"),
    path("create_products/", views.ProductCreateViewAPI.as_view() , name="create_products"),
    path("reservations_search/", views.ReservationSearchAPI.as_view(), name="reservation_search"),
    path("coffeehouse-map-page/", views.CoffeehousesMapAPIView.as_view(), name="map-page"),
    path("get-coffeehouses/", views.CoffeehouseFormApiView.as_view(), name="get-coffeehouses"),
    path("get-booking-duration/", views.GetBookingDuration.as_view(), name="get-booking-duration"),
    path("get-tables/", views.GetTablesReservation.as_view(), name="get-tables"),
    path("user_profile/", views.ProfileInfoAPI.as_view(), name="user_profile"),
    path("user_history_reservations/", views.ProfileHitoryAPI.as_view(), name="user_history_reservations"),
    path("create_reservation/", views.CreateReservationAPI.as_view(), name="create_reservation"),
]
