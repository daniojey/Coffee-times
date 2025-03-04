import re
from rest_framework import serializers
from coffeehouses.models import Product
from orders.models import Reservation

class ProductSerializer(serializers.ModelSerializer):
    adds_by = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name','category', 'price', 'discount', 'adds_by']
        
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


