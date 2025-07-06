import json
import logging
from django.http import JsonResponse
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import status

logger = logging.getLogger(__name__)


class AuthenticationMiddleware:
    """Middleware для аутентификации запросов к микросервисам"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Пропускаем health check и swagger
        if request.path in ['/health/', '/swagger/', '/redoc/'] or request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # Пропускаем аутентификационные endpoints
        if request.path.startswith('/api/v1/auth/'):
            return self.get_response(request)
        
        # Проверяем JWT токен для API запросов
        if request.path.startswith('/api/v1/'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if not auth_header.startswith('Bearer '):
                return JsonResponse({
                    'error': 'Требуется аутентификация',
                    'detail': 'Необходим Bearer токен'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(' ')[1]
            
            try:
                # Валидируем токен
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Добавляем информацию о пользователе в request
                request.user_id = user_id
                request.user_authenticated = True
                
                logger.info(f"Аутентифицированный запрос от пользователя {user_id} к {request.path}")
                
            except (InvalidToken, TokenError) as e:
                logger.warning(f"Недействительный токен: {e}")
                return JsonResponse({
                    'error': 'Недействительный токен',
                    'detail': str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return self.get_response(request)


class AuthorizationMiddleware:
    """Middleware для авторизации и проверки прав доступа"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Пропускаем неаутентифицированные запросы
        if not hasattr(request, 'user_authenticated') or not request.user_authenticated:
            return self.get_response(request)
        
        # Проверяем права доступа к различным сервисам
        if request.path.startswith('/api/v1/users/'):
            # Для User Service требуются права администратора
            if not self._has_admin_permission(request):
                return JsonResponse({
                    'error': 'Недостаточно прав',
                    'detail': 'Требуются права администратора'
                }, status=status.HTTP_403_FORBIDDEN)
        
        elif request.path.startswith('/api/v1/finance/'):
            # Для Finance Service требуются права финансового менеджера
            if not self._has_finance_permission(request):
                return JsonResponse({
                    'error': 'Недостаточно прав',
                    'detail': 'Требуются права финансового менеджера'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return self.get_response(request)
    
    def _has_admin_permission(self, request):
        """Проверка прав администратора"""
        # Здесь должна быть логика проверки прав из User Service
        # Пока возвращаем True для демонстрации
        return True
    
    def _has_finance_permission(self, request):
        """Проверка прав финансового менеджера"""
        # Здесь должна быть логика проверки прав из User Service
        # Пока возвращаем True для демонстрации
        return True


class RequestLoggingMiddleware:
    """Middleware для логирования запросов"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Логируем входящий запрос
        logger.info(f"Входящий запрос: {request.method} {request.path} от {self._get_client_ip(request)}")
        
        response = self.get_response(request)
        
        # Логируем исходящий ответ
        logger.info(f"Исходящий ответ: {response.status_code} для {request.method} {request.path}")
        
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 