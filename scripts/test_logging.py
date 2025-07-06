#!/usr/bin/env python3
"""
Скрипт для тестирования логирования с эмодзи на Windows
"""

import os
import sys
import logging

# Добавляем путь к Django проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')

import django
django.setup()

from core.utils import send_business_alert, send_error_alert
from core.logging_handlers import setup_windows_logging

def test_logging():
    """
    Тестирует логирование с эмодзи
    """
    print("🧪 Тестирование логирования с эмодзи...")
    
    # Настраиваем Windows-совместимое логирование
    is_windows = setup_windows_logging()
    print(f"🌐 Операционная система: {'Windows' if is_windows else 'Unix/Linux'}")
    
    # Получаем логгер
    logger = logging.getLogger(__name__)
    
    # Тестируем различные сообщения с эмодзи
    test_messages = [
        "🔐 Пользователь вошел в систему",
        "⏰ Время: 2025-07-06 20:31:48",
        "📄 Описание: Тестовое сообщение",
        "👤 Пользователь: Test User",
        "🚨 Критическая ошибка!",
        "⚠️ Предупреждение системы",
        "✅ Операция выполнена успешно",
        "❌ Операция завершилась неудачей",
        "💰 Финансовая операция: 1000 ₽",
        "📝 Заметка: Важная информация",
        "🔗 Ссылка: https://example.com",
        "📋 Детали: Подробная информация",
        "ℹ️ Информация: Общие сведения",
        "📢 Объявление: Системное уведомление"
    ]
    
    print("\n📝 Тестирование логирования в файл...")
    for i, message in enumerate(test_messages, 1):
        logger.info(f"Тест {i}: {message}")
        print(f"  ✅ Логировано: {message}")
    
    print("\n🔔 Тестирование Telegram уведомлений...")
    try:
        # Тестируем бизнес-алерт
        success = send_business_alert(
            event_type="test",
            description="Тестовое уведомление с эмодзи 🔐⏰📄👤",
            user_info="Test User",
            additional_data={"test": "data"}
        )
        print(f"  {'✅' if success else '❌'} Бизнес-алерт отправлен")
        
        # Тестируем алерт об ошибке
        test_error = Exception("Тестовая ошибка с эмодзи 🚨⚠️❌")
        success = send_error_alert(
            error=test_error,
            request_path="/test/",
            user_info="Test User",
            additional_info={"test": "error"}
        )
        print(f"  {'✅' if success else '❌'} Алерт об ошибке отправлен")
        
    except Exception as e:
        print(f"  ❌ Ошибка при отправке Telegram: {e}")
    
    print("\n📊 Проверка лог-файлов...")
    log_files = [
        "logs/django.log",
        "logs/alerts.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"  ✅ Файл {log_file} создан")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  📄 Размер: {len(content)} символов")
                    if '🔐' in content or '[LOGIN]' in content:
                        print(f"  ✅ Эмодзи или их замены найдены в логе")
                    else:
                        print(f"  ⚠️ Эмодзи не найдены в логе")
            except Exception as e:
                print(f"  ❌ Ошибка чтения файла: {e}")
        else:
            print(f"  ❌ Файл {log_file} не найден")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_logging() 