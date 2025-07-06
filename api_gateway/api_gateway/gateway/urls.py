from django.urls import path, re_path
from .views import user_service_proxy, zayavki_service_proxy, finance_service_proxy, health_check

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
    # User Service routes
    path('api/v1/users/', user_service_proxy, name='user_service_root'),
    re_path(r'^api/v1/users/(?P<path>.*)$', user_service_proxy, name='user_service_proxy'),
    
    # Zayavki Service routes
    path('api/v1/zayavki/', zayavki_service_proxy, name='zayavki_service_root'),
    re_path(r'^api/v1/zayavki/(?P<path>.*)$', zayavki_service_proxy, name='zayavki_service_proxy'),
    
    # Finance Service routes
    path('api/v1/finance/', finance_service_proxy, name='finance_service_root'),
    re_path(r'^api/v1/finance/(?P<path>.*)$', finance_service_proxy, name='finance_service_proxy'),
] 