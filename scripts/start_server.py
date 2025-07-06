#!/usr/bin/env python
"""
Скрипт для запуска Django сервера с правильными настройками
"""

import os
import sys
import django

# Настройка переменных окружения
os.environ.setdefault('SECRET_KEY', 'your-super-secret-key-for-testing-12345')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('DB_NAME', 'CRM')
os.environ.setdefault('DB_USER', 'postgres')
os.environ.setdefault('DB_PASSWORD', '1740')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('REDIS_AVAILABLE', 'False')  # Используем локальный кэш
os.environ.setdefault('ALERTS_ENABLED', 'False')
os.environ.setdefault('ENVIRONMENT', 'development')

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')

def main():
    """Запуск Django сервера"""
    print("🚀 Запуск Django сервера CRM с системой мониторинга")
    print("=" * 60)
    
    try:
        # Инициализация Django
        django.setup()
        print("✅ Django инициализирован успешно")
        
        # Проверяем основные компоненты
        from django.core.cache import cache
        print("✅ Кэш настроен")
        
        from core.monitoring import alert_manager, performance_monitor, database_monitor
        print("✅ Система мониторинга загружена")
        
        # Тестируем кэш
        try:
            cache.set('server_test', 'ok', 10)
            test_value = cache.get('server_test')
            if test_value == 'ok':
                print("✅ Кэш работает корректно")
            else:
                print("⚠️ Кэш работает с ошибками")
        except Exception as e:
            print(f"⚠️ Кэш недоступен: {e}")
        
        print("\n📋 Доступные endpoints:")
        print("  • http://localhost:8000/api/health/ - Базовый health check")
        print("  • http://localhost:8000/api/health/detailed/ - Детальная диагностика")
        print("  • http://localhost:8000/api/metrics/ - Метрики системы")
        print("  • http://localhost:8000/api/monitoring/performance/ - Метрики производительности")
        print("  • http://localhost:8000/api/monitoring/alerts/ - История алертов")
        print("  • http://localhost:8000/api/monitoring/status/ - Статус системы")
        
        print("\n🔧 Запуск сервера...")
        print("💡 Для остановки нажмите Ctrl+C")
        print("-" * 60)
        
        # Запускаем сервер
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
        
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 