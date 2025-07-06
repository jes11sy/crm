import logging
from django.conf import settings

class TelegramLogHandler(logging.Handler):
    """
    Кастомный лог-хендлер для отправки сообщений в Telegram
    """
    
    def __init__(self, level=logging.ERROR):
        super().__init__(level)
        self.enabled = getattr(settings, 'TELEGRAM_ALERTS_ENABLED', True)
        self.error_alerts = getattr(settings, 'TELEGRAM_ERROR_ALERTS', True)
    
    def emit(self, record):
        if not self.enabled or not self.error_alerts:
            return
        try:
            # Ленивая загрузка функций, чтобы избежать проблем с инициализацией Django
            from core.utils import send_telegram_alert, format_error_alert
            # Форматируем сообщение
            message = self.format(record)
            # Если это ошибка, отправляем специально отформатированное сообщение
            if record.levelno >= logging.ERROR:
                request_path = getattr(record, 'request_path', '')
                user_info = getattr(record, 'user_info', '')
                additional_info = getattr(record, 'additional_info', {})
                error = getattr(record, 'exc_info', None)
                if error and error[1]:
                    error_obj = error[1]
                else:
                    error_obj = Exception(record.getMessage())
                formatted_message = format_error_alert(
                    error=error_obj,
                    request_path=request_path,
                    user_info=user_info,
                    additional_info=additional_info
                )
            else:
                formatted_message = message
            send_telegram_alert(formatted_message)
        except Exception as e:
            import sys
            print(f"Failed to send Telegram alert: {e}", file=sys.stderr) 