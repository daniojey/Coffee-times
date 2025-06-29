"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from rest_framework.routers import DefaultRouter
from api.views import CustomTokenVerifyView,CustomTokenRefreshView, CustomTokenObtainPairView, ProductViewSets, ProfileHitoryAPI, ProfileInfoAPI, ReservationSearchAPI
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


router = DefaultRouter()
router.register(r"products", ProductViewSets)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('coffeehouses.urls',namespace='coffeehouses')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('user/', include('users.urls', namespace='users')),
    path('api/<str:version>/', include(router.urls)),
    path('api/v1/', include('api.urls', namespace='api')),
    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    
]  

# +  debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)