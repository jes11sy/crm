#!/usr/bin/env python3
"""
Скрипт для генерации безопасного Django SECRET_KEY
"""

import secrets
import string
import sys

def generate_secret_key(length=50):
    """Генерирует безопасный SECRET_KEY для Django"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Убираем символы, которые могут вызвать проблемы в .env файлах
    alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '')
    
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

def main():
    """Основная функция"""
    print("🔐 Генерация безопасного Django SECRET_KEY")
    print("=" * 50)
    
    # Генерируем ключ
    secret_key = generate_secret_key()
    
    print(f"✅ Сгенерирован новый SECRET_KEY:")
    print(f"SECRET_KEY={secret_key}")
    print()
    
    # Сохраняем в файл
    try:
        with open('.env.local', 'w') as f:
            f.write(f"SECRET_KEY={secret_key}\n")
        print("✅ SECRET_KEY сохранен в файл .env.local")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить в файл: {e}")
    
    print()
    print("📋 Инструкции:")
    print("1. Скопируйте SECRET_KEY выше")
    print("2. Добавьте его в переменные окружения вашего сервера")
    print("3. Или добавьте в файл .env для локальной разработки")
    print("4. НИКОГДА не коммитьте SECRET_KEY в git!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 