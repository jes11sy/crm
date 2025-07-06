import time
import logging
from django.db import connection
from django.conf import settings
from django.http import HttpResponseRedirect
from .monitoring import alert_manager, performance_monitor
from .utils import send_error_alert

logger = logging.getLogger(__name__)

class APIVersionRedirectMiddleware:
    """Middleware для редиректа API запросов на версионированные endpoints"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Проверяем, является ли это API запросом без версии
        if request.path.startswith('/api/') and not request.path.startswith('/api/v'):
            # Исключаем специальные endpoints
            excluded_paths = [
                '/api/schema/',
                '/api/docs/',
                '/api/redoc/',
                '/api/mango-audio-files/',
            ]
            
            if not any(request.path.startswith(path) for path in excluded_paths):
                # Редиректим на v1
                new_path = request.path.replace('/api/', '/api/v1/', 1)
                return HttpResponseRedirect(new_path)
        
        return self.get_response(request)

class QueryCountDebugMiddleware:
    """Middleware для подсчета SQL запросов в DEBUG режиме"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)
        
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        response = self.get_response(request)
        
        end_time = time.time()
        duration = end_time - start_time
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        
        # Логируем информацию о запросах
        logger.info(
            f'Request: {request.method} {request.path} - '
            f'Queries: {query_count}, Time: {duration:.3f}s'
        )
        
        # Записываем метрики производительности
        performance_monitor.record_request_time(
            request.path, 
            request.method, 
            duration, 
            response.status_code
        )
        
        # Проверяем критические пороги
        if query_count > 50:  # Слишком много запросов
            alert_manager.log_error(
                'HIGH_QUERY_COUNT',
                f'Too many database queries: {query_count}',
                {
                    'path': request.path,
                    'method': request.method,
                    'query_count': query_count,
                    'duration': duration
                }
            )
        
        if duration > 5.0:  # Медленный запрос
            alert_manager.log_error(
                'SLOW_REQUEST',
                f'Slow request: {duration:.3f}s',
                {
                    'path': request.path,
                    'method': request.method,
                    'duration': duration,
                    'query_count': query_count
                }
            )
        
        if response.status_code >= 500:  # Серверная ошибка
            alert_manager.log_error(
                'SERVER_ERROR',
                f'Server error {response.status_code}',
                {
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'duration': duration
                }
            )
        
        return response


class PerformanceMonitoringMiddleware:
    """Middleware для мониторинга производительности"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Исключаем определенные endpoints из мониторинга производительности
        excluded_endpoints = [
            '/api/login/', 
            '/api/logout/', 
            '/api/clear-cookies/',
            '/api/me/',
            '/api/health/',
            '/api/health/detailed/',
            '/api/metrics/',
            '/api/monitoring/performance/',
            '/api/monitoring/alerts/',
            '/api/monitoring/status/'
        ]
        
        if request.path not in excluded_endpoints:
            # Записываем метрики только для основных endpoints
            performance_monitor.record_request_time(
                request.path,
                request.method,
                duration,
                response.status_code
            )
        
        # Добавляем заголовки с метриками (только в DEBUG)
        if settings.DEBUG:
            response['X-Response-Time'] = f'{duration:.3f}s'
            response['X-Query-Count'] = str(len(connection.queries))
        
        return response


class ErrorHandlingMiddleware:
    """Middleware для обработки ошибок и алертов"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Получаем информацию о пользователе
            user_info = "Неавторизованный"
            if hasattr(request, 'user') and request.user.is_authenticated:
                if hasattr(request.user, 'username'):
                    user_info = request.user.username
                elif hasattr(request.user, 'phone'):
                    user_info = request.user.phone
            
            # Логируем необработанную ошибку
            logger.error(f'Unhandled exception in {request.path}: {e}', exc_info=True)
            
            # Отправляем алерт в систему мониторинга
            alert_manager.log_error(
                'UNHANDLED_EXCEPTION',
                str(e),
                {
                    'path': request.path,
                    'method': request.method,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'remote_addr': request.META.get('REMOTE_ADDR', '')
                }
            )
            
            # Отправляем Telegram-алерт
            if getattr(settings, 'TELEGRAM_ALERTS_ENABLED', True):
                send_error_alert(
                    error=e,
                    request_path=request.path,
                    user_info=user_info,
                    additional_info={
                        'method': request.method,
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'remote_addr': request.META.get('REMOTE_ADDR', ''),
                        'query_params': dict(request.GET.items()),
                        'post_data': dict(request.POST.items()) if request.method == 'POST' else {}
                    }
                )
            
            # Возвращаем ошибку 500
            from django.http import JsonResponse
            return JsonResponse({
                'error': 'Внутренняя ошибка сервера',
                'code': 'INTERNAL_ERROR'
            }, status=500)


class SecurityMonitoringMiddleware:
    """Middleware для мониторинга безопасности"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Проверяем подозрительную активность
        self._check_suspicious_activity(request)
        
        response = self.get_response(request)
        
        # Проверяем ответ на уязвимости
        self._check_response_security(response, request)
        
        return response
    
    def _check_suspicious_activity(self, request):
        """Проверка подозрительной активности"""
        # Исключаем endpoints авторизации и мониторинга из проверок безопасности
        excluded_endpoints = [
            '/api/login/', 
            '/api/logout/', 
            '/api/clear-cookies/',
            '/api/me/',
            '/api/health/',
            '/api/health/detailed/',
            '/api/metrics/',
            '/api/monitoring/performance/',
            '/api/monitoring/alerts/',
            '/api/monitoring/status/'
        ]
        if request.path in excluded_endpoints:
            return
        
        # Проверяем частоту запросов
        client_ip = request.META.get('REMOTE_ADDR', '')
        request_key = f'request_count_{client_ip}'
        
        try:
            from django.core.cache import cache
            request_count = cache.get(request_key, 0) + 1
            cache.set(request_key, request_count, 60)  # 1 минута
            
            if request_count > 100:  # Слишком много запросов с одного IP
                alert_manager.log_error(
                    'RATE_LIMIT_EXCEEDED',
                    f'Too many requests from IP: {client_ip}',
                    {
                        'ip': client_ip,
                        'request_count': request_count,
                        'path': request.path,
                        'user_agent': request.META.get('HTTP_USER_AGENT', '')
                    }
                )
        except Exception as e:
            # Если кэш недоступен, логируем ошибку но не прерываем запрос
            logger.warning(f'Cache unavailable for rate limiting: {e}')
            # Можно добавить fallback логику здесь
        
        # Проверяем подозрительные заголовки
        suspicious_headers = ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP']
        for header in suspicious_headers:
            if header in request.META:
                alert_manager.log_error(
                    'SUSPICIOUS_HEADER',
                    f'Suspicious header detected: {header}',
                    {
                        'header': header,
                        'value': request.META[header],
                        'ip': client_ip,
                        'path': request.path
                    }
                )
    
    def _check_response_security(self, response, request):
        """Проверка безопасности ответа"""
        # Исключаем все API endpoints из проверки заголовков безопасности
        # так как они добавляются позже в SecurityHeadersMiddleware
        if request.path.startswith('/api/'):
            return
        
        # Проверяем отсутствие важных заголовков безопасности
        security_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection'
        ]
        
        missing_headers = []
        for header in security_headers:
            if header not in response:
                missing_headers.append(header)
        
        if missing_headers:
            alert_manager.log_error(
                'MISSING_SECURITY_HEADERS',
                f'Missing security headers: {missing_headers}',
                {
                    'missing_headers': missing_headers,
                    'path': request.path,
                    'method': request.method
                }
            ) 

class SecurityHeadersMiddleware:
    """Middleware для принудительного добавления заголовков безопасности"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Принудительно добавляем заголовки безопасности
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp_policy
        
        return response 