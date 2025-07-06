from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipZayavkiViewSet, ZayavkaViewSet, ZayavkaFileViewSet

router = DefaultRouter()
router.register(r'tipzayavki', TipZayavkiViewSet, basename='tipzayavki')
router.register(r'zayavki', ZayavkaViewSet, basename='zayavki')
router.register(r'zayavkafiles', ZayavkaFileViewSet, basename='zayavkafiles')

urlpatterns = [
    path('api/v1/', include(router.urls)),
] 