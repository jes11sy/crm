from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipTranzakciiViewSet, TranzakciyaViewSet, PayoutViewSet

router = DefaultRouter()
router.register(r'tiptranzakcii', TipTranzakciiViewSet, basename='tiptranzakcii')
router.register(r'tranzakcii', TranzakciyaViewSet, basename='tranzakcii')
router.register(r'payouts', PayoutViewSet, basename='payouts')

urlpatterns = [
    path('api/v1/', include(router.urls)),
] 