"""
URL-маршруты для API микросервиса пользователей
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GorodViewSet, RoliViewSet, PolzovateliViewSet, MasterViewSet

router = DefaultRouter()
router.register(r'gorods', GorodViewSet)
router.register(r'rolis', RoliViewSet)
router.register(r'polzovatelis', PolzovateliViewSet)
router.register(r'masters', MasterViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
] 