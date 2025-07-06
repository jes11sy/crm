import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class AlertManager:
    """Менеджер алертов для критических ошибок"""
    
    def __init__(self):
        self.alert_cache_key = 'crm_alerts'
        self.alert_threshold = 5  # Количество ошибок перед отправкой алерта
        self.alert_cooldown = 300  # 5 минут между алертами
    
    def log_error(self, error_type, error_message, context=None):
        """Логирование ошибки и проверка необходимости алерта"""
        timestamp = datetime.now().isoformat()
        
        # Логируем ошибку
        logger.error(f'{error_type}: {error_message}', extra={
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {},
            'timestamp': timestamp
        })
        
        # Проверяем необходимость алерта
        self._check_alert_threshold(error_type, error_message, context, timestamp)
    
    def _check_alert_threshold(self, error_type, error_message, context, timestamp):
        """Проверка порога ошибок для отправки алерта"""
        try:
            alert_key = f'alert_count_{error_type}'
            last_alert_key = f'last_alert_{error_type}'
            
            # Увеличиваем счетчик ошибок
            current_count = cache.get(alert_key, 0) + 1
            cache.set(alert_key, current_count, 3600)  # Храним 1 час
            
            # Проверяем время последнего алерта
            last_alert = cache.get(last_alert_key)
            if last_alert and (datetime.now() - last_alert).seconds < self.alert_cooldown:
                return
            
            # Если достигли порога, отправляем алерт
            if current_count >= self.alert_threshold:
                self._send_alert(error_type, error_message, context, current_count, timestamp)
                cache.set(last_alert_key, datetime.now(), 3600)
                cache.set(alert_key, 0, 3600)  # Сбрасываем счетчик
        except Exception as e:
            # Если кэш недоступен, отправляем алерт без rate limiting
            logger.warning(f'Cache unavailable for alert threshold: {e}')
            self._send_alert(error_type, error_message, context, 1, timestamp)
    
    def _send_alert(self, error_type, error_message, context, count, timestamp):
        """Отправка алерта"""
        try:
            # Проверяем настройки алертов
            if not getattr(settings, 'ALERTS_ENABLED', False):
                return
            
            alert_data = {
                'type': error_type,
                'message': error_message,
                'count': count,
                'timestamp': timestamp,
                'context': context or {},
                'environment': getattr(settings, 'ENVIRONMENT', 'development')
            }
            
            # Отправляем через email
            if getattr(settings, 'ALERT_EMAIL_ENABLED', False):
                self._send_email_alert(alert_data)
            
            # Отправляем через webhook
            if getattr(settings, 'ALERT_WEBHOOK_URL', None):
                self._send_webhook_alert(alert_data)
            
            # Сохраняем в лог алертов
            self._log_alert(alert_data)
            
        except Exception as e:
            logger.error(f'Failed to send alert: {e}')
    
    def _send_email_alert(self, alert_data):
        """Отправка алерта по email"""
        try:
            smtp_host = getattr(settings, 'SMTP_HOST', 'localhost')
            smtp_port = getattr(settings, 'SMTP_PORT', 587)
            smtp_user = getattr(settings, 'SMTP_USER', '')
            smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
            alert_emails = getattr(settings, 'ALERT_EMAILS', [])
            
            if not alert_emails:
                return
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ', '.join(alert_emails)
            msg['Subject'] = f'[CRM ALERT] {alert_data["type"]} - {alert_data["environment"]}'
            
            body = f"""
Критическая ошибка в CRM системе!

Тип ошибки: {alert_data['type']}
Сообщение: {alert_data['message']}
Количество повторений: {alert_data['count']}
Время: {alert_data['timestamp']}
Окружение: {alert_data['environment']}

Контекст: {json.dumps(alert_data['context'], indent=2, ensure_ascii=False)}

Проверьте логи системы для получения дополнительной информации.
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user and smtp_password:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
                
            logger.info(f'Alert email sent to {alert_emails}')
            
        except Exception as e:
            logger.error(f'Failed to send email alert: {e}')
    
    def _send_webhook_alert(self, alert_data):
        """Отправка алерта через webhook"""
        try:
            webhook_url = getattr(settings, 'ALERT_WEBHOOK_URL')
            webhook_headers = getattr(settings, 'ALERT_WEBHOOK_HEADERS', {})
            
            response = requests.post(
                webhook_url,
                json=alert_data,
                headers=webhook_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f'Webhook alert sent successfully')
            else:
                logger.error(f'Webhook alert failed with status {response.status_code}')
                
        except Exception as e:
            logger.error(f'Failed to send webhook alert: {e}')
    
    def _log_alert(self, alert_data):
        """Сохранение алерта в лог"""
        try:
            alert_log_file = os.path.join(settings.BASE_DIR, 'logs', 'alerts.log')
            os.makedirs(os.path.dirname(alert_log_file), exist_ok=True)
            
            with open(alert_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {json.dumps(alert_data, ensure_ascii=False)}\n")
                
        except Exception as e:
            logger.error(f'Failed to log alert: {e}')


class PerformanceMonitor:
    """Мониторинг производительности"""
    
    def __init__(self):
        self.metrics_cache_key = 'crm_performance_metrics'
    
    def record_request_time(self, endpoint, method, duration, status_code):
        """Запись времени выполнения запроса"""
        try:
            metrics = cache.get(self.metrics_cache_key, {})
            
            key = f"{method}_{endpoint}"
            if key not in metrics:
                metrics[key] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0,
                    'error_count': 0,
                    'last_updated': datetime.now().isoformat()
                }
            
            metric = metrics[key]
            metric['count'] += 1
            metric['total_time'] += duration
            metric['avg_time'] = metric['total_time'] / metric['count']
            metric['min_time'] = min(metric['min_time'], duration)
            metric['max_time'] = max(metric['max_time'], duration)
            
            if status_code >= 400:
                metric['error_count'] += 1
            
            metric['last_updated'] = datetime.now().isoformat()
            
            # Храним метрики 24 часа
            cache.set(self.metrics_cache_key, metrics, 86400)
            
        except Exception as e:
            logger.error(f'Failed to record performance metric: {e}')
            # Если кэш недоступен, продолжаем работу без метрик
    
    def get_performance_metrics(self):
        """Получение метрик производительности"""
        try:
            metrics = cache.get(self.metrics_cache_key, {})
            
            # Добавляем общую статистику
            total_requests = sum(m['count'] for m in metrics.values())
            total_errors = sum(m['error_count'] for m in metrics.values())
            avg_response_time = sum(m['avg_time'] for m in metrics.values()) / len(metrics) if metrics else 0
            
            return {
                'endpoints': metrics,
                'summary': {
                    'total_requests': total_requests,
                    'total_errors': total_errors,
                    'error_rate': (total_errors / total_requests * 100) if total_requests > 0 else 0,
                    'avg_response_time': avg_response_time,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f'Failed to get performance metrics: {e}')
            # Возвращаем пустые метрики если кэш недоступен
            return {
                'endpoints': {},
                'summary': {
                    'total_requests': 0,
                    'total_errors': 0,
                    'error_rate': 0,
                    'avg_response_time': 0,
                    'timestamp': datetime.now().isoformat(),
                    'cache_error': str(e)
                }
            }


class DatabaseMonitor:
    """Мониторинг базы данных"""
    
    def __init__(self):
        self.db_metrics_key = 'crm_db_metrics'
    
    def check_database_health(self):
        """Проверка здоровья базы данных"""
        try:
            from django.db import connection
            from django.db.utils import OperationalError
            
            start_time = datetime.now()
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Проверяем количество активных соединений
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """)
                active_connections = cursor.fetchone()[0]
            
            metrics = {
                'status': 'healthy',
                'response_time_ms': response_time,
                'active_connections': active_connections,
                'timestamp': datetime.now().isoformat()
            }
            
            # Сохраняем метрики
            cache.set(self.db_metrics_key, metrics, 300)  # 5 минут
            
            return metrics
            
        except OperationalError as e:
            error_metrics = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            cache.set(self.db_metrics_key, error_metrics, 300)
            return error_metrics
        except Exception as e:
            logger.error(f'Database health check failed: {e}')
            return {'status': 'unknown', 'error': str(e)}


# Глобальные экземпляры
alert_manager = AlertManager()
performance_monitor = PerformanceMonitor()
database_monitor = DatabaseMonitor() 