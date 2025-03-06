from django.urls import path



from . import views

app_name = 'api'

urlpatterns = [
    path("reservations_search/", views.ReservationSearchAPI.as_view(), name="reservation_search"),
    path("user_profile/", views.ProfileInfoAPI.as_view(), name="user_profile"),
    path("user_history_reservations/", views.ProfileHitoryAPI.as_view(), name="user_history_reservations"),
    path("create_reservation/", views.CreateReservationAPI.as_view(), name="create_reservation"),
]
