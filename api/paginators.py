from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status

class CustomHistoryPagination(PageNumberPagination):
    page_size = 4  # дефолтное значение элементов на странице
    page_size_query_param = 'page_size'  # параметр для изменения количества элементов
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'items_per_page': self.page_size,  # добавляем информацию о количестве
            'results': data
        }, status=status.HTTP_200_OK)