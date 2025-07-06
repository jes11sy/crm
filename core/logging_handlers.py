"""
Кастомные хендлеры для логирования с поддержкой UTF-8
"""

import logging
import sys
import os
from typing import Optional


class SafeUTF8FileHandler(logging.FileHandler):
    """
    Безопасный файловый хендлер с поддержкой UTF-8 и обработкой эмодзи
    """
    
    def __init__(self, filename: str, mode: str = 'a', encoding: str = 'utf-8', 
                 delay: bool = False, errors: Optional[str] = None):
        super().__init__(filename, mode, encoding, delay, errors)
    
    def emit(self, record):
        """
        Переопределяем emit для безопасной обработки сообщений с эмодзи
        """
        try:
            # Безопасно обрабатываем сообщение
            safe_msg = self._sanitize_message(record.getMessage())
            record.msg = safe_msg
            record.args = ()  # Очищаем аргументы, так как сообщение уже обработано
            
            super().emit(record)
        except Exception:
            # Если что-то пошло не так, логируем в stderr
            try:
                sys.stderr.write(f"Logging error: {record.getMessage()}\n")
                sys.stderr.flush()
            except:
                pass
    
    def _sanitize_message(self, message: str) -> str:
        """
        Безопасно обрабатывает сообщение, заменяя проблемные символы
        """
        if not isinstance(message, str):
            return str(message)
        
        # Заменяем эмодзи на безопасные символы
        emoji_replacements = {
            '🔐': '[LOGIN]',
            '⏰': '[TIME]',
            '📄': '[DESC]',
            '👤': '[USER]',
            '🚨': '[ERROR]',
            '⚠️': '[WARNING]',
            '✅': '[SUCCESS]',
            '❌': '[FAIL]',
            '💰': '[MONEY]',
            '📝': '[NOTE]',
            '🔗': '[LINK]',
            '📋': '[DETAILS]',
            'ℹ️': '[INFO]',
            '📢': '[ALERT]',
        }
        
        for emoji, replacement in emoji_replacements.items():
            message = message.replace(emoji, replacement)
        
        # Для Windows: оставляем все символы, так как файл записывается в UTF-8
        return message


class ConsoleHandler(logging.StreamHandler):
    """
    Консольный хендлер с поддержкой UTF-8
    """
    
    def __init__(self, stream=None):
        if stream is None:
            # Используем stderr для ошибок, stdout для остального
            stream = sys.stdout
        super().__init__(stream)
        
        # Устанавливаем кодировку для Windows
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8', errors='replace')
            except:
                pass
    
    def emit(self, record):
        """
        Переопределяем emit для безопасной обработки
        """
        try:
            # Безопасно обрабатываем сообщение
            safe_msg = self._sanitize_message(record.getMessage())
            record.msg = safe_msg
            record.args = ()
            
            super().emit(record)
        except Exception:
            # Если что-то пошло не так, выводим в stderr
            try:
                sys.stderr.write(f"Console logging error: {record.getMessage()}\n")
                sys.stderr.flush()
            except:
                pass
    
    def _sanitize_message(self, message: str) -> str:
        """
        Безопасно обрабатывает сообщение для консоли
        """
        if not isinstance(message, str):
            return str(message)
        
        # Заменяем эмодзи на текстовые эквиваленты
        emoji_replacements = {
            '🔐': '[LOGIN]',
            '⏰': '[TIME]',
            '📄': '[DESC]',
            '👤': '[USER]',
            '🚨': '[ERROR]',
            '⚠️': '[WARNING]',
            '✅': '[SUCCESS]',
            '❌': '[FAIL]',
            '💰': '[MONEY]',
            '📝': '[NOTE]',
            '🔗': '[LINK]',
            '📋': '[DETAILS]',
            'ℹ️': '[INFO]',
            '📢': '[ALERT]',
        }
        
        for emoji, replacement in emoji_replacements.items():
            message = message.replace(emoji, replacement)
        
        return message


def setup_windows_logging():
    """
    Настройка логирования для Windows с поддержкой UTF-8
    """
    import logging.config
    
    # Проверяем, работаем ли мы на Windows
    is_windows = os.name == 'nt'
    
    if is_windows:
        # Настраиваем кодировку для stdout и stderr
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except:
            pass
        
        # Устанавливаем переменную окружения для Python
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    return is_windows 