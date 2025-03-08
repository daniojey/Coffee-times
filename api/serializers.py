from datetime import datetime, timedelta
import re
from django.db.models import F, Q, ExpressionWrapper, TimeField
from rest_framework import serializers
from coffeehouses.models import CoffeeHouse, Product, Table
from orders.models import Reservation

class ProductSerializer(serializers.ModelSerializer):
    adds_by = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'description','category', 'price', 'discount', 'adds_by']
        
        extra_kwargs = {
            'name': {'required': True},
            'description': {'required': False},
        }

    def get_adds_by(self, obj):
        request = self.context.get('request')
        return request.user.username if request else None
    

class ReservationSerializer(serializers.ModelSerializer):
    coffeehouse_name = serializers.CharField(source='coffeehouse.name', read_only=True)
    table_number = serializers.IntegerField(source="table.table_number", read_only=True)

    status_display = serializers.SerializerMethodField()
    streaming_status = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields =  [
            'id', 'coffeehouse_name', 'table_number', 'customer_name', 'customer_phone',
            'reservation_date', 'reservation_time', 'booking_duration', 'created_at',
            'status_display' ,'streaming_status', 'created_ip'
        ]
        extra_kwargs = {
            'created_ip': {'read_only': True},
            'created_at': {'read_only': True},
            'status': {'read_only': True},
        }

    def get_status_display(self, obj):
        return "Успішне" if obj.status == True else "Не успішне"
    
    def get_streaming_status(self, obj):
        return obj.get_status()

    def validate_customer_phone(self, value):
        """Валидация номера телефона резервации"""
        if not value.startwith("380") or value.startwith("+380"):
            raise serializers.ValidationError("Телефон неверного формата, начало должно быть 380 либо +380")
        return value
    
    def create(self, validated_data):
        """При сохранении автоматически добавляем ip"""
        request = self.context.get('request')
        validated_data['created_ip'] = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return super().create(validated_data) 
    




class ReservationProfileSericalizer(serializers.ModelSerializer):
    coffeehouse_name = serializers.CharField(source='coffeehouse.name', read_only=True)
    status_res = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            "coffeehouse_name", 'reservation_date', 'reservation_time', 'status_res'
        ]

    def get_status_res(self, obj):
        return obj.get_status()


class ReservationCreateSerializer(serializers.ModelSerializer):
    coffeehouse = serializers.PrimaryKeyRelatedField(queryset=CoffeeHouse.objects.all(), required=True)
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), required=True)

    class Meta:
        model = Reservation
        fields = [
            'coffeehouse', 'table', 'customer_name', 'customer_phone',
            'reservation_date', 'reservation_time', 'booking_duration'
        ]

    def validate_customer_phone(self, value):
        """Валидация номера телефона"""
        if not re.match(r"^\+?380\d{9}$", value):
            raise serializers.ValidationError("Номер телефона должен быть формата 380 либо +380")
        return value
    
    def validate(self, data):
        """Проверка занятости столика в указанное время"""
        coffeehouse = data["coffeehouse"]
        table = data["table"]
        reservation_date = data["reservation_date"]
        reservation_time = data["reservation_time"]
        booking_duration = data["booking_duration"]

        print(coffeehouse)
        print(coffeehouse.opening_time)
        print(coffeehouse.closing_time)

        if reservation_time > coffeehouse.closing_time or reservation_time < coffeehouse.opening_time:
            message = f"Данное время недопустимо, доступный промежуток времени кофейни {coffeehouse.opening_time}|{coffeehouse.closing_time}"
            raise serializers.ValidationError(str(message))

        # Переводим данные в `datetime`
        reservation_time_obj = datetime.strptime(str(reservation_time), "%H:%M:%S").time()
        print(reservation_time_obj)
        h2, m2 = divmod(booking_duration.seconds, 3600)
        print(h2, m2)
        reservation_datetime = datetime.combine(reservation_date, reservation_time_obj)
        print(reservation_datetime)
        delta2 = timedelta(minutes=h2, seconds=m2)
        print(delta2)
        total_time = reservation_datetime + delta2
        print(total_time)
        end_time = total_time.time()
        print(end_time)

        # Проверяем занятость столика
        existing_reservations = Reservation.objects.filter(
            coffeehouse=coffeehouse, table=table, reservation_date=reservation_date
        ).annotate(
            end_time=ExpressionWrapper(F('reservation_time') + F('booking_duration'), output_field=TimeField())
        )

        print(reservation_time)
        print(booking_duration)
        print(end_time)

        conflict = existing_reservations.filter(
            Q(end_time__gt=reservation_time) & Q(reservation_time__lt=end_time) 
        ).exists()
        
        if conflict:
            raise serializers.ValidationError("Столик уже забронирован на это время, выберите другое.")
        
        return data
    
    def create(self, validated_data):
        """Создание резервации с учётом авторизованного пользователя"""
        request = self.context.get('request')
        ip = self.context.get('ip')

        if request.user.is_authenticated:
            validated_data['customer_name'] = request.user.username
            validated_data['customer_phone'] = request.user.phone

        validated_data['created_ip'] = ip
        return super().create(validated_data)