from django.utils.timezone import now
from django.db.models import Q

from orders.models import Reservation

def get_actual_reservations(phone):
    print(now().time())
    return Reservation.objects.filter(
        Q(customer_phone=phone) &
        Q(reservation_date__gte=now().date())
    ).exclude(
        Q(reservation_date=now().date(), reservation_time__lt=now().time()) 
    ).order_by('reservation_date', 'reservation_time')

