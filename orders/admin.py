from django.contrib import admin
from django.db.models import Avg, Count, Sum
from django.urls import path
from django.views.generic import TemplateView

from orders.models import Reservation
from unfold.admin import ModelAdmin
from django.db.models.functions import TruncMonth
from unfold.views import UnfoldModelAdminViewMixin

# @admin.register(Reservation)
# class ReservationClass(ModelAdmin):
#     list_filter_submit = True
#     list_filter = [
#         ("customer_phone", FieldTextFilter),
#         ("customer_name", FieldTextFilter),
        
#     ]
# admin.site.register(Reservation)

class ReservationStatisticsView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Статистика резерваций"
    permission_required = ()
    template_name = "admin/reservation_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем данные по месяцам
        monthly_stats = Reservation.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_reservations=Count('id')
        ).order_by('month')

        # Подготавливаем данные для графика
        labels = []
        data = []
        
        for stat in monthly_stats:
            labels.append(stat['month'].strftime('%b %Y'))
            data.append(stat['total_reservations'])

        context.update({
            'labels': labels,
            'data': data,
        })
        
        return context

@admin.register(Reservation)
class ReservationModelAdmin(ModelAdmin):
    list_select_related = ["coffeehouse", "table"]
    list_display = ["coffeehouse", "get_table_seats", "customer_name", "customer_phone", "reservation_date", "reservation_time", "booking_duration", "created_at"]

    def get_table_seats(self, obj):
        return obj.table.table_number
    get_table_seats.short_description = 'Количество мест'  # Название в админке

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'statistics/',
                self.admin_site.admin_view(ReservationStatisticsView.as_view(model_admin=self)),
                name='reservation_statistics'
            ),
        ]

        return my_urls + urls  # my_urls должны быть ПЕРВЫМИ