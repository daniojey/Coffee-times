from django.utils.timezone import now
from django.db.models import Q

from orders.models import Reservation

def get_actual_reservations(phone=None, ip=None):
    print(now().time())
    if phone:
        res =Reservation.objects.filter(
            Q(customer_phone=phone) &
            Q(reservation_date__gte=now().date())
        ).exclude(
            Q(reservation_date=now().date(), reservation_time__lt=now().time()) 
        ).order_by('reservation_date', 'reservation_time')
    elif ip:
        res =Reservation.objects.filter(
            Q(created_ip=ip) &
            Q(reservation_date__gte=now().date())
        ).exclude(
            Q(reservation_date=now().date(), reservation_time__lt=now().time()) 
        ).order_by('reservation_date', 'reservation_time')
    else:
        res = []
    
    return res


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip