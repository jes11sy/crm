from rest_framework.views import APIView
from rest_framework.response import Response
import platform
import django
from django.conf import settings
from django.core.cache import cache
import logging
import psutil
import os
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..utils import send_telegram_alert, send_error_alert, send_business_alert

# HealthCheckView, DetailedHealthCheckView, MetricsView, PerformanceMetricsView, AlertHistoryView, SystemStatusView
# (перенести соответствующие классы из views.py) 

logger = logging.getLogger(__name__)

class HealthCheckView(APIView):
    permission_classes = []
    def get(self, request):
        try:
            # Базовая проверка здоровья системы
            health_status = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'version': {
                    'django': django.get_version(),
                    'python': platform.python_version(),
                    'platform': platform.platform()
                },
                'database': 'ok',
                'cache': 'ok'
            }
            
            # Проверка базы данных
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                health_status['database'] = 'ok'
            except Exception as e:
                health_status['database'] = 'error'
                health_status['status'] = 'unhealthy'
                logger.error(f"Database health check failed: {e}")
            
            # Проверка кэша
            try:
                cache.set('health_check', 'ok', 60)
                if cache.get('health_check') == 'ok':
                    health_status['cache'] = 'ok'
                else:
                    health_status['cache'] = 'error'
                    health_status['status'] = 'unhealthy'
            except Exception as e:
                health_status['cache'] = 'error'
                health_status['status'] = 'unhealthy'
                logger.error(f"Cache health check failed: {e}")
            
            return Response(health_status)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response({
                'status': 'unhealthy',
                'error': str(e)
            }, status=500)

class DetailedHealthCheckView(APIView):
    permission_classes = []
    def get(self, request):
        try:
            # Детальная проверка здоровья системы
            detailed_status = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'system': {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent
                },
                'application': {
                    'django_version': django.get_version(),
                    'python_version': platform.python_version(),
                    'platform': platform.platform()
                },
                'services': {
                    'database': 'ok',
                    'cache': 'ok',
                    'filesystem': 'ok'
                }
            }
            
            # Проверка базы данных
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                detailed_status['services']['database'] = 'ok'
            except Exception as e:
                detailed_status['services']['database'] = 'error'
                detailed_status['status'] = 'unhealthy'
                logger.error(f"Database detailed health check failed: {e}")
            
            # Проверка кэша
            try:
                cache.set('detailed_health_check', 'ok', 60)
                if cache.get('detailed_health_check') == 'ok':
                    detailed_status['services']['cache'] = 'ok'
                else:
                    detailed_status['services']['cache'] = 'error'
                    detailed_status['status'] = 'unhealthy'
            except Exception as e:
                detailed_status['services']['cache'] = 'error'
                detailed_status['status'] = 'unhealthy'
                logger.error(f"Cache detailed health check failed: {e}")
            
            # Проверка файловой системы
            try:
                test_file = '/tmp/health_check_test'
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                detailed_status['services']['filesystem'] = 'ok'
            except Exception as e:
                detailed_status['services']['filesystem'] = 'error'
                detailed_status['status'] = 'unhealthy'
                logger.error(f"Filesystem health check failed: {e}")
            
            return Response(detailed_status)
            
        except Exception as e:
            logger.error(f"Detailed health check failed: {e}")
            return Response({
                'status': 'unhealthy',
                'error': str(e)
            }, status=500)

class MetricsView(APIView):
    permission_classes = []
    def get(self, request):
        try:
            # Сбор метрик производительности
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'system': {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                'process': {
                    'pid': os.getpid(),
                    'memory_info': psutil.Process().memory_info()._asdict(),
                    'cpu_percent': psutil.Process().cpu_percent()
                }
            }
            
            return Response(metrics)
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return Response({'error': str(e)}, status=500)

class PerformanceMetricsView(APIView):
    permission_classes = []
    def get(self, request):
        try:
            # Получение метрик производительности
            performance_metrics = {
                'timestamp': timezone.now().isoformat(),
                'system_performance': {
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'network_io': psutil.net_io_counters()._asdict()
                },
                'application_metrics': {
                    'django_version': django.get_version(),
                    'python_version': platform.python_version()
                }
            }
            
            return Response(performance_metrics)
            
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {e}")
            return Response({'error': str(e)}, status=500)

class AlertHistoryView(APIView):
    permission_classes = []
    def get(self, request):
        try:
            # Получение истории алертов
            # Здесь должна быть логика получения алертов из базы данных или логов
            alert_history = {
                'timestamp': timezone.now().isoformat(),
                'alerts': [
                    # Пример алертов
                    {
                        'id': 1,
                        'level': 'warning',
                        'message': 'High CPU usage detected',
                        'timestamp': timezone.now().isoformat()
                    }
                ]
            }
            
            return Response(alert_history)
            
        except Exception as e:
            logger.error(f"Alert history retrieval failed: {e}")
            return Response({'error': str(e)}, status=500)

class SystemStatusView(APIView):
    permission_classes = []
    def get(self, request):
        try:
            # Получение общего статуса системы
            system_status = {
                'timestamp': timezone.now().isoformat(),
                'overall_status': 'operational',
                'components': {
                    'database': 'operational',
                    'cache': 'operational',
                    'filesystem': 'operational',
                    'network': 'operational'
                },
                'system_info': {
                    'platform': platform.platform(),
                    'python_version': platform.python_version(),
                    'django_version': django.get_version(),
                    'uptime': timezone.now() - timezone.now()  # Здесь должна быть реальная логика
                }
            }
            
            # Проверка компонентов
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                system_status['components']['database'] = 'operational'
            except Exception as e:
                system_status['components']['database'] = 'degraded'
                system_status['overall_status'] = 'degraded'
                logger.error(f"Database status check failed: {e}")
            
            try:
                cache.set('system_status_check', 'ok', 60)
                if cache.get('system_status_check') == 'ok':
                    system_status['components']['cache'] = 'operational'
                else:
                    system_status['components']['cache'] = 'degraded'
                    system_status['overall_status'] = 'degraded'
            except Exception as e:
                system_status['components']['cache'] = 'degraded'
                system_status['overall_status'] = 'degraded'
                logger.error(f"Cache status check failed: {e}")
            
            return Response(system_status)
            
        except Exception as e:
            logger.error(f"System status check failed: {e}")
            return Response({
                'overall_status': 'degraded',
                'error': str(e)
            }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_telegram_alert(request):
    """
    Тестирует отправку алертов в Telegram
    """
    alert_type = request.data.get('type', 'info')
    message = request.data.get('message', 'Тестовое сообщение')
    
    if not getattr(settings, 'TELEGRAM_ALERTS_ENABLED', True):
        return Response({
            'error': 'Telegram алерты отключены'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if alert_type == 'error':
            # Тестируем отправку ошибки
            error = Exception(message)
            success = send_error_alert(
                error=error,
                request_path=request.path,
                user_info=request.user.username if hasattr(request.user, 'username') else str(request.user),
                additional_info={
                    'test': True,
                    'user_id': request.user.id
                }
            )
        elif alert_type == 'business':
            # Тестируем бизнес-событие
            success = send_business_alert(
                event_type='test_event',
                description=message,
                user_info=request.user.username if hasattr(request.user, 'username') else str(request.user),
                additional_data={
                    'test': True,
                    'user_id': request.user.id,
                    'timestamp': '2025-07-06 10:45:00'
                }
            )
        else:
            # Простое сообщение
            success = send_telegram_alert(
                f"🧪 <b>ТЕСТОВОЕ СООБЩЕНИЕ</b>\n\n"
                f"📄 <b>Сообщение:</b> {message}\n"
                f"👤 <b>Пользователь:</b> {request.user.username if hasattr(request.user, 'username') else str(request.user)}\n"
                f"⏰ <b>Время:</b> {request.data.get('timestamp', 'Сейчас')}"
            )
        
        if success:
            return Response({
                'success': True,
                'message': f'Telegram алерт типа "{alert_type}" отправлен успешно'
            })
        else:
            return Response({
                'error': 'Не удалось отправить Telegram алерт'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f'Error testing Telegram alert: {e}')
        return Response({
            'error': f'Ошибка при тестировании: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_test_error(request):
    """
    Искусственно вызывает ошибку для тестирования алертов
    """
    try:
        # Искусственно вызываем ошибку
        raise Exception("Тестовая ошибка для проверки алертов")
    except Exception as e:
        # Ошибка будет обработана middleware и отправлена в Telegram
        raise e 