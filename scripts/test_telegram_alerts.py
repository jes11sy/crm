#!/usr/bin/env python3
"""
Скрипт для тестирования Telegram-алертов
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from core.utils import send_telegram_alert, send_error_alert, send_business_alert

def test_simple_message():
    """Тестирует отправку простого сообщения"""
    print("🧪 Тестирование простого сообщения...")
    
    message = f"🧪 <b>ТЕСТОВОЕ СООБЩЕНИЕ</b>\n\n"
    message += f"📄 <b>Сообщение:</b> Простое тестовое сообщение\n"
    message += f"⏰ <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"🔧 <b>Тип:</b> Простое сообщение"
    
    success = send_telegram_alert(message)
    
    if success:
        print("✅ Простое сообщение отправлено успешно!")
    else:
        print("❌ Ошибка отправки простого сообщения")
    
    return success

def test_error_alert():
    """Тестирует отправку алерта об ошибке"""
    print("\n🚨 Тестирование алерта об ошибке...")
    
    # Создаем тестовую ошибку
    error = Exception("Тестовая ошибка для проверки алертов")
    
    success = send_error_alert(
        error=error,
        request_path="/api/test/endpoint",
        user_info="test_user (admin)",
        additional_info={
            'test': True,
            'method': 'POST',
            'ip_address': '127.0.0.1',
            'user_agent': 'TestScript/1.0'
        }
    )
    
    if success:
        print("✅ Алерт об ошибке отправлен успешно!")
    else:
        print("❌ Ошибка отправки алерта об ошибке")
    
    return success

def test_business_alert():
    """Тестирует отправку бизнес-события"""
    print("\n📝 Тестирование бизнес-события...")
    
    success = send_business_alert(
        event_type='new_zayavka',
        description='Создана новая заявка #12345',
        user_info='test_user (admin)',
        additional_data={
            'zayavka_id': 12345,
            'gorod': 'Москва',
            'tip_zayavki': 'Ремонт',
            'client_phone': '+7 (999) 123-45-67',
            'test': True
        }
    )
    
    if success:
        print("✅ Бизнес-событие отправлено успешно!")
    else:
        print("❌ Ошибка отправки бизнес-события")
    
    return success

def test_api_endpoint():
    """Тестирует API endpoint для алертов"""
    print("\n🌐 Тестирование API endpoint...")
    
    # URL для тестирования (предполагаем, что сервер запущен на localhost:8000)
    base_url = "http://localhost:8000/api/v1"
    
    # Сначала нужно получить токен (логин)
    login_data = {
        "login": "admin",  # Замените на реальный логин
        "password": "admin"  # Замените на реальный пароль
    }
    
    try:
        # Логин
        login_response = requests.post(f"{base_url}/login/", json=login_data)
        
        if login_response.status_code == 200:
            print("✅ Успешный логин")
            
            # Получаем cookies
            cookies = login_response.cookies
            
            # Тестируем endpoint для алертов
            test_data = {
                "type": "info",
                "message": "Тестовое сообщение через API",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            alert_response = requests.post(
                f"{base_url}/test-telegram-alert/",
                json=test_data,
                cookies=cookies
            )
            
            if alert_response.status_code == 200:
                result = alert_response.json()
                print(f"✅ API тест успешен: {result.get('message', '')}")
                return True
            else:
                print(f"❌ API тест неудачен: {alert_response.status_code}")
                print(f"Ответ: {alert_response.text}")
                return False
        else:
            print(f"❌ Ошибка логина: {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу. Убедитесь, что Django сервер запущен.")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования Telegram-алертов")
    print("=" * 50)
    
    # Проверяем настройки
    from django.conf import settings
    
    print(f"📋 Настройки:")
    print(f"   - TELEGRAM_ALERTS_ENABLED: {getattr(settings, 'TELEGRAM_ALERTS_ENABLED', False)}")
    print(f"   - TELEGRAM_BOT_TOKEN: {'Настроен' if getattr(settings, 'TELEGRAM_BOT_TOKEN', None) else 'Не настроен'}")
    print(f"   - TELEGRAM_CHAT_ID: {'Настроен' if getattr(settings, 'TELEGRAM_CHAT_ID', None) else 'Не настроен'}")
    print()
    
    if not getattr(settings, 'TELEGRAM_ALERTS_ENABLED', False):
        print("⚠️  Telegram алерты отключены в настройках")
        return
    
    if not getattr(settings, 'TELEGRAM_BOT_TOKEN', None) or not getattr(settings, 'TELEGRAM_CHAT_ID', None):
        print("⚠️  Не настроены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
        return
    
    # Запускаем тесты
    results = []
    
    results.append(test_simple_message())
    results.append(test_error_alert())
    results.append(test_business_alert())
    
    # Тестируем API endpoint (если сервер запущен)
    print("\n" + "=" * 50)
    print("🌐 Тестирование API endpoints (требует запущенный сервер)")
    results.append(test_api_endpoint())
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    
    successful_tests = sum(results)
    total_tests = len(results)
    
    print(f"   - Всего тестов: {total_tests}")
    print(f"   - Успешных: {successful_tests}")
    print(f"   - Неудачных: {total_tests - successful_tests}")
    
    if successful_tests == total_tests:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️  Некоторые тесты не прошли. Проверьте настройки и логи.")

if __name__ == "__main__":
    main() 