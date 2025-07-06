from django.shortcuts import render
import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def proxy_request(service_url, path, method='GET', data=None, headers=None):
    """Прокси-функция для перенаправления запросов к микросервисам"""
    try:
        url = f"{service_url}{path}"
        response = requests.request(
            method=method,
            url=url,
            json=data if method in ['POST', 'PUT', 'PATCH'] else None,
            params=data if method == 'GET' else None,
            headers=headers or {},
            timeout=30
        )
        return JsonResponse(
            response.json() if response.headers.get('content-type', '').startswith('application/json') else {'data': response.text},
            status=response.status_code,
            safe=False
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying request to {service_url}: {e}")
        return JsonResponse(
            {'error': f'Service unavailable: {str(e)}'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user_service_proxy(request, path=''):
    """Прокси для User Service"""
    service_url = settings.MICROSERVICES['user_service']
    return proxy_request(service_url, f'/api/v1/{path}', request.method, request.data)

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def zayavki_service_proxy(request, path=''):
    """Прокси для Zayavki Service"""
    service_url = settings.MICROSERVICES['zayavki_service']
    return proxy_request(service_url, f'/api/v1/{path}', request.method, request.data)

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def finance_service_proxy(request, path=''):
    """Прокси для Finance Service"""
    service_url = settings.MICROSERVICES['finance_service']
    return proxy_request(service_url, f'/api/v1/{path}', request.method, request.data)

@api_view(['GET'])
def health_check(request):
    """Проверка здоровья API Gateway"""
    services_status = {}
    
    for service_name, service_url in settings.MICROSERVICES.items():
        try:
            response = requests.get(f"{service_url}/admin/", timeout=5)
            services_status[service_name] = 'healthy' if response.status_code < 500 else 'unhealthy'
        except:
            services_status[service_name] = 'unavailable'
    
    return Response({
        'status': 'healthy',
        'services': services_status
    })
