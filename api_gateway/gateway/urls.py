from django.urls import path
from . import views

app_name = 'gateway'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health'),
    
    # Прокси к User Service
    path('users/', views.user_service_proxy, name='user_service_proxy'),
    path('users/<path:path>', views.user_service_proxy, name='user_service_proxy_detail'),
    
    # Прокси к Zayavki Service
    path('zayavki/', views.zayavki_service_proxy, name='zayavki_service_proxy'),
    path('zayavki/<path:path>', views.zayavki_service_proxy, name='zayavki_service_proxy_detail'),
    
    # Прокси к Finance Service
    path('finance/', views.finance_service_proxy, name='finance_service_proxy'),
    path('finance/<path:path>', views.finance_service_proxy, name='finance_service_proxy_detail'),
] 