import requests
import logging
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check для API Gateway"""
    services_status = {
        'api_gateway': 'healthy',
        'user_service': 'unknown',
        'zayavki_service': 'unknown',
        'finance_service': 'unknown'
    }
    
    # Проверяем статус микросервисов
    try:
        response = requests.get(f"{settings.USER_SERVICE_URL}/health/", timeout=5)
        services_status['user_service'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services_status['user_service'] = 'unreachable'
    
    try:
        response = requests.get(f"{settings.ZAYAVKI_SERVICE_URL}/health/", timeout=5)
        services_status['zayavki_service'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services_status['zayavki_service'] = 'unreachable'
    
    try:
        response = requests.get(f"{settings.FINANCE_SERVICE_URL}/health/", timeout=5)
        services_status['finance_service'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services_status['finance_service'] = 'unreachable'
    
    return Response({
        'status': 'healthy',
        'service': 'api_gateway',
        'services': services_status
    })


def user_service_proxy(request, path=''):
    """Прокси к User Service"""
    return _proxy_request(request, settings.USER_SERVICE_URL, path)


def zayavki_service_proxy(request, path=''):
    """Прокси к Zayavki Service"""
    return _proxy_request(request, settings.ZAYAVKI_SERVICE_URL, path)


def finance_service_proxy(request, path=''):
    """Прокси к Finance Service"""
    return _proxy_request(request, settings.FINANCE_SERVICE_URL, path)


def _proxy_request(request, service_url, path=''):
    """Общая функция для проксирования запросов"""
    # Формируем URL для микросервиса
    if path:
        target_url = f"{service_url}/api/v1/{path}"
    else:
        target_url = f"{service_url}/api/v1/"
    
    # Подготавливаем заголовки
    headers = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_') and key != 'HTTP_HOST':
            header_name = key[5:].replace('_', '-').title()
            headers[header_name] = value
    
    # Добавляем информацию о пользователе, если аутентифицирован
    if hasattr(request, 'user_id'):
        headers['X-User-ID'] = str(request.user_id)
    
    try:
        # Выполняем запрос к микросервису
        if request.method == 'GET':
            response = requests.get(target_url, headers=headers, params=request.GET, timeout=30)
        elif request.method == 'POST':
            response = requests.post(target_url, headers=headers, json=request.data, timeout=30)
        elif request.method == 'PUT':
            response = requests.put(target_url, headers=headers, json=request.data, timeout=30)
        elif request.method == 'PATCH':
            response = requests.patch(target_url, headers=headers, json=request.data, timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(target_url, headers=headers, timeout=30)
        else:
            return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
        
        # Логируем запрос
        logger.info(f"Прокси запрос: {request.method} {target_url} -> {response.status_code}")
        
        # Возвращаем ответ от микросервиса
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return JsonResponse(response_data, status=response.status_code)
        
    except requests.exceptions.Timeout:
        logger.error(f"Таймаут при обращении к {target_url}")
        return JsonResponse({
            'error': 'Таймаут сервиса',
            'detail': 'Микросервис не отвечает'
        }, status=503)
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Ошибка подключения к {target_url}")
        return JsonResponse({
            'error': 'Сервис недоступен',
            'detail': 'Не удается подключиться к микросервису'
        }, status=503)
        
    except Exception as e:
        logger.error(f"Ошибка проксирования: {e}")
        return JsonResponse({
            'error': 'Внутренняя ошибка',
            'detail': str(e)
        }, status=500) 