#!/usr/bin/env python3
"""
Скрипт для запуска Django сервера с SSL поддержкой
"""

import os
import sys
import subprocess
from pathlib import Path

def check_ssl_certs():
    """Проверка наличия SSL сертификатов"""
    cert_dir = Path("ssl_certs")
    key_file = cert_dir / "localhost.key"
    cert_file = cert_dir / "localhost.crt"
    
    if not key_file.exists() or not cert_file.exists():
        print("❌ SSL сертификаты не найдены")
        print("Запустите: python scripts/generate_ssl_cert.py")
        return False
    
    print("✅ SSL сертификаты найдены")
    return True

def install_django_extensions():
    """Установка django-extensions для SSL поддержки"""
    try:
        import django_extensions
        print("✅ django-extensions уже установлен")
        return True
    except ImportError:
        print("📦 Установка django-extensions...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "django-extensions"], check=True)
            print("✅ django-extensions установлен")
            return True
        except subprocess.CalledProcessError:
            print("❌ Ошибка при установке django-extensions")
            return False

def start_ssl_server():
    """Запуск Django сервера с SSL"""
    
    print("🔐 Запуск Django сервера с SSL...")
    print("=" * 50)
    
    # Проверяем SSL сертификаты
    if not check_ssl_certs():
        return False
    
    # Устанавливаем django-extensions
    if not install_django_extensions():
        return False
    
    # Добавляем django-extensions в INSTALLED_APPS
    settings_file = Path("panel/settings.py")
    if settings_file.exists():
        with open(settings_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "django_extensions" not in content:
            # Добавляем django_extensions в INSTALLED_APPS
            content = content.replace(
                "INSTALLED_APPS = [",
                "INSTALLED_APPS = [\n    'django_extensions',"
            )
            
            with open(settings_file, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ django_extensions добавлен в INSTALLED_APPS")
    
    # Запускаем сервер с SSL
    try:
        cmd = [
            sys.executable, "manage.py", "runserver_plus",
            "--cert-file", "ssl_certs/localhost.crt",
            "--key-file", "ssl_certs/localhost.key",
            "--addrport", "0.0.0.0:8000"
        ]
        
        print("🚀 Запуск сервера...")
        print(f"Команда: {' '.join(cmd)}")
        print("💡 Откройте: https://localhost:8000")
        print("💡 Для остановки нажмите Ctrl+C")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    
    print("🔐 Django SSL Server для CRM")
    print("=" * 50)
    
    # Проверяем, что мы в корневой директории проекта
    if not Path("manage.py").exists():
        print("❌ Файл manage.py не найден")
        print("Запустите скрипт из корневой директории проекта")
        return
    
    # Запускаем сервер
    start_ssl_server()

if __name__ == "__main__":
    main() 