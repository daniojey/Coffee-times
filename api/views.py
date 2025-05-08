from datetime import datetime, timedelta
import re
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Q, ExpressionWrapper
from django.http import JsonResponse
from rest_framework import viewsets, status
from api.paginators import CustomHistoryPagination
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from api.permission import IsAdminOrReadOnly, IsUserOrReadOnly
from users.utils import get_actual_reservations, get_user_ip
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.views.decorators.http import require_GET
from orders.models import Reservation
from coffeehouses.models import Category, Product
from users.models import User

@require_GET
def get_csrf_token(request):
    return JsonResponse({"csrfToken": request.META.get('CSRF_COOKIE')})


class LoginViewApi(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return Response({'Status': 'success'})
        else:
            return Response({'message': 'Неверный логин либо парроль'}, status=status.HTTP_403_FORBIDDEN)
        

class RegistrationViewApi(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        phone = request.data.get('phone')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')

        if not username or not phone or not password1 or not password2:
            return Response({'error': 'Не заповнені усі поля'}, status=status.HTTP_400_BAD_REQUEST)
        
        if password1 != password2:
            return Response({'error': 'Пароли не співпадають'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(phone) < 10 or len(phone) > 15:
            return Response({'error': 'Невірний номер телефона'}, status=status.HTTP_400_BAD_REQUEST)

        pattern = r'^(?:380|0)\d{9}$'
        if re.match(pattern, phone):
            if phone[0] == '0':
                phone = '38' + phone
            
            if User.objects.filter(Q(username=username) | Q(phone=phone)).exists():
                return Response({'error': 'Користувач з таким логіном або номером телефону вже існує'}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"error": "Невірний формат номеру телефону"}, status=status.HTTP_400_BAD_REQUEST)
        
        User.objects.create_user(username=username, phone=phone, password=password1)

        user = authenticate(request, username=username, password=password1)
        if user:
            login(request, user)
        return Response({'status': 'Аккаунт створено!'}, status=status.HTTP_201_CREATED)
    

class CheckAuthUserViewApi(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({ 'user': {'id': request.user.id, 'username': request.user.username} })
        else:
            return JsonResponse({'user': None})
        

class UserLogoutViewApi(APIView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Пользователь не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)
            
        logout(request)
        return Response({"status": "Success"}, status=status.HTTP_200_OK)


class ProductViewSets(viewsets.ModelViewSet):
    queryset =  Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = (IsAdminUser,)

    def get_serializer_context(self):
        """Передаем текущего пользователя в сериализатор"""
        return {'request': self.request}
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response({'results': serializer.data})
    
class ProductHomePageApiView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.all()[:5]
        serializer = serializers.ProductSerializer(queryset, many=True, context={'request': request})
        return Response({'products': serializer.data}, status=status.HTTP_200_OK)


class ProductMenuPageAPI(APIView):
    def get(self, request, *args, **kwargs):
        search = request.GET.get('search');
        category = request.GET.get('category');

        products = Product.objects.all().select_related('category')

        if search:
            products = products.filter(name__icontains=search)

        if category:
            products = products.filter(category__name=category)

        paginator = CustomHistoryPagination()
        result_page = paginator.paginate_queryset(products, request)

        if result_page is not None:
            serializer = serializers.ProductSerializer(result_page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        return Response({'products': []}, status=status.HTTP_200_OK)


class ProductCategoryAPI(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = serializers.CategorySerializer(categories, many=True)
        return Response({'categories': serializer.data}, status=status.HTTP_200_OK)
    

class ProductCreateViewAPI(APIView):

    def post(self, request, *args, **kwargs):
        serializer = serializers.ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Продукт успешно создан', 'product': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationSearchAPI(APIView):
    # permission_classes = (IsAdminOrReadOnly, )
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
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.phone:
            actual_reservations = get_actual_reservations(username=user.username)
        else:
            actual_reservations = get_actual_reservations(phone=user.phone)

        actual_res_list = set(actual_reservations.values_list('id', flat=True)[:2])
        actual_res_queryset = Reservation.objects.filter(id__in=actual_res_list)
        reservations = Reservation.objects.filter(Q(customer_name=user.username) | Q(customer_phone=user.phone)).exclude(id__in=actual_res_list).select_related('coffeehouse').order_by('-reservation_date')[:3]

        serializer_actual_res = serializers.ReservationProfileSericalizer(actual_res_queryset, many=True)
        serializer_reservations = serializers.ReservationProfileSericalizer(reservations, many=True)

        user_data = {
            'username': user.username,
            'phone': user.phone if user.phone else None,
        }

        return Response({'reservations': serializer_reservations.data, 'actual_reservations': serializer_actual_res.data, 'user_data': user_data}, status=status.HTTP_200_OK)
        


class ProfileHitoryAPI(APIView):
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
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

        paginator = CustomHistoryPagination()
        result_page = paginator.paginate_queryset(reservations, request)
        if result_page is not None:
            serializer = serializers.ReservationProfileSericalizer(result_page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)

        return Response({'reservations': []}, status=status.HTTP_200_OK)
    


class CreateReservationAPI(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        ip = get_user_ip(request)

        # Передаём request в сериализатор для получения контекста
        serializer = serializers.ReservationCreateSerializer(data=request.data, context={'request': request, 'ip': ip})

        # Проверка данных
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Бронирование успешно созданно', 'reservation': serializer.data}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)