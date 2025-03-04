import re
from rest_framework import viewsets, status

from users.utils import get_actual_reservations
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from orders.models import Reservation

from coffeehouses.models import Product

class ProductViewSets(viewsets.ModelViewSet):
    queryset =  Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_serializer_context(self):
        """Передаем текущего пользователя в сериализатор"""
        return {'request': self.request}
    


class ReservationSearchAPI(APIView):
    """АPI для поиска резервации по номеру телефона"""
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')

        if not phone:
            return Response({'error': 'По цьому номеру немає резервацій'}, status=status.HTTP_400_BAD_REQUEST)
        
        if phone[0] == "0":
            phone = "38" + phone

        
        pattern = r'^(?:380|0)\d{9}$'
        if not re.match(pattern, phone):
            return Response({"error": "Невірний номер телефону, перевірте будь ласка правильність введеного номеру"}, status=status.HTTP_400_BAD_REQUEST)
        
        reservations = Reservation.objects.filter(customer_phone=phone).select_related('coffeehouse', 'table').order_by('-reservation_date')

        serializer = serializers.ReservationSerializer(reservations, many=True)
        return Response({'reservations': serializer.data}, status=status.HTTP_200_OK)
    
    def get(self, request, *args, **kwargs):
        reservations = Reservation.objects.none()
        serializer = serializers.ReservationSerializer(reservations, many=True)
        return Response({'reservations': serializer.data}, status=status.HTTP_200_OK)
    

class ProfileInfoAPI(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.phone:
            actual_reservations = get_actual_reservations(username=user.username)
        else:
            actual_reservations = get_actual_reservations(phone=user.phone)

        actual_res_list = set(actual_reservations.values_list('id', flat=True)[:2])
        actual_res_queryset = Reservation.objects.filter(id__in=actual_res_list)
        reservations = Reservation.objects.filter(customer_name=user.username, customer_phone=user.phone).exclude(id__in=actual_res_list).select_related('coffeehouse').order_by('-reservation_date')[:3]

        serializer_actual_res = serializers.ReservationProfileSericalizer(actual_res_queryset, many=True)
        serializer_reservations = serializers.ReservationProfileSericalizer(reservations, many=True)
        return Response({'reservations': serializer_reservations.data, 'actual_reservations': serializer_actual_res.data}, status=status.HTTP_200_OK)
        


class ProfileHitoryAPI(APIView):
    def get(self, request, *args, **kwargs):
        s_active = request.GET.get("is_active", '')
        s_coffeehouse = request.GET.get('is_cafe', '')
        s_sort_by = request.GET.get("sort_by", '')
        
        user = request.user

        if user.phone:
            reservations = Reservation.objects.filter(customer_phone=user.phone).select_related('coffeehouse')
        else:
            reservations = Reservation.objects.filter(customer_name=user.username).select_related('coffeehouse')

        if s_active:
            if user.phone:
                reservations = get_actual_reservations(phone=user.phone)
            else:
                reservations = get_actual_reservations(username=user.username)

        if s_coffeehouse:
            reservations = reservations.order_by("coffeehouse")


        if s_sort_by:
            if s_sort_by == 'date':
                reservations = reservations.order_by('-reservation_date')
            elif s_sort_by == 'time':
                reservations = reservations.order_by('reservation_time')

        serrializer = serializers.ReservationProfileSericalizer(reservations, many=True)
        return Response({'reservations': serrializer.data}, status=status.HTTP_200_OK)