from datetime import datetime, timedelta
import re
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Q, ExpressionWrapper, TimeField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
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
from coffeehouses.models import Category, CoffeeHouse, Product, Table
from users.models import User
from django.middleware.csrf import get_token

@require_GET
def get_csrf_token(request):
    response = JsonResponse({"detail": "CSRF cookie set"})
    response["X-CSRFToken"] = get_token(request)
    print(response)
    return response

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
    

class CoffeehousesMapAPIView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = CoffeeHouse.objects.all()
        serializer = serializers.CoffeehousesMapSerializer(queryset, many=True, context={"request": request})

        return Response({'results': serializer.data})


class ReservationSearchAPI(APIView):
    # permission_classes = (IsAdminOrReadOnly, )
    """АPI для поиска резервации по номеру телефона"""
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        actual = request.data.get('actual')

        print(phone)
        print(actual)
        print(request.data)

        if not phone:
            return Response({'error': 'По цьому номеру немає резервацій'}, status=status.HTTP_400_BAD_REQUEST)
        
        if phone[0] == "0":
            phone = "38" + phone

        
        pattern = r'^(?:380|0)\d{9}$'
        if not re.match(pattern, phone):
            return Response({"error": "Невірний номер телефону, перевірте будь ласка правильність введеного номеру"}, status=status.HTTP_400_BAD_REQUEST)
        
        if actual:
            reservations = get_actual_reservations(phone=phone)
        else:
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

        print(s_active)
        print(s_coffeehouse)
        print(s_sort_by)
        
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


class GetBookingDuration(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data

            coffeehouse_id = data.get('coffeehouse')
            reservation_time = data.get('reservation_time')

            coffeehouse = get_object_or_404(CoffeeHouse, id=coffeehouse_id)

            # Преобразуем время закрытия и время бронирования в datetime
            closing_time = datetime.strptime(coffeehouse.closing_time.strftime("%H:%M"), "%H:%M")
            reservation_time = datetime.strptime(reservation_time, "%H:%M")

            # Вычисляем разницу между временем закрытия и временем бронирования
            difference = closing_time - reservation_time

            if difference.total_seconds() <= 0:
                # Если разница отрицательная или равна 0, бронирование невозможно
                return JsonResponse({'data': ["00:00"]})

            # Получаем оставшиеся часы и минуты
            remaining_hours, remainder = divmod(difference.seconds, 3600)
            remaining_minutes = remainder // 60

            durations = []

            # Генерация доступных интервалов времени
            if remaining_hours <= 3:
                for hour in range(remaining_hours + 1):
                    for minute in range(0, 60, 15):  # Интервалы по 15 минут
                        if hour == remaining_hours and minute > remaining_minutes:
                            break  # Прерываем, если минуты выходят за пределы оставшегося времени
                        elif hour > 4 and minute > remaining_minutes:
                            break

                        durations.append(f"{hour:02}:{minute:02}")
            else:
                for hour in range(4):
                    for minute in range(0, 60, 15):  # Интервалы по 15 минут
                        if hour == 3 and minute > 0:
                            break
                        durations.append(f"{hour:02}:{minute:02}")

            if len(durations) == 0:
                durations.append("00:00")

            return Response({'data': durations}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Ошибка", e)
            return Response({'error': f'Ошибка логики {e}'}, status=status.HTTP_400_BAD_REQUEST)


class GetTablesReservation(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Парсим данные из тела запроса
            data = request.data
            coffeehouse_id = data.get('coffeehouse')
            reservation_date = data.get('reservation_date')
            reservation_time = data.get('reservation_time')
            booking_duration = data.get('booking_duration')

            reservations_today = Reservation.objects.filter(coffeehouse_id=coffeehouse_id ,reservation_date=reservation_date).select_related('table')
            for item in reservations_today:
                print(item.table)

            annotations_reservation = reservations_today.annotate(
                end_time=ExpressionWrapper(
                    F('reservation_time') + F('booking_duration'),
                    output_field=TimeField()
                )
            )
 
            for reservation in annotations_reservation:
                print(reservation.end_time)


            # Преобразуем reservation_time в объект времени
            reservation_time_obj = datetime.strptime(reservation_time, "%H:%M").time()

            # Преобразуем booking_duration в timedelta
            hours, minutes = map(int, booking_duration.split(":"))
            booking_duration_td = timedelta(hours=hours, minutes=minutes)

            # Объединяем reservation_date и reservation_time для получения datetime
            reservation_datetime = datetime.combine(datetime.strptime(reservation_date, "%Y-%m-%d"), reservation_time_obj)

            # Добавляем продолжительность
            end_datetime = reservation_datetime + booking_duration_td

            # Извлекаем только время окончания
            end_time = end_datetime.time()

             # Фильтруем пересекающиеся брони
            overlapping_reservations = annotations_reservation.filter(end_time__gt=reservation_time).filter(reservation_time__lt=end_time).values_list('table_id', flat=True)


            # Формируем данные для ответа
            tables_data = [{"id": table.id, 'name': table.table_number} for table in Table.objects.filter(coffeehouse_id=coffeehouse_id).exclude(id__in=overlapping_reservations)]
            request.session['coffeehouse'] = coffeehouse_id
            return Response({'tables': tables_data}, status=status.HTTP_200_OK)

        except Exception as e:
            print('ОШИБКА', e)
            return Response({'error': f'Invalid JSON data {e}'}, status=status.HTTP_400_BAD_REQUEST)
        

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
    

class CoffeehouseFormApiView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = CoffeeHouse.objects.all()
        serializer = serializers.CoffeehouseFormSerializer(queryset, many=True)

        if serializer:
            return Response({ 'coffeehouses': serializer.data }, status=status.HTTP_200_OK)
        
        return Response({'coffeehouses': []}, status=status.HTTP_200_OK)