#!/usr/bin/env python3
"""
Скрипт для генерации SSL сертификатов для разработки
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_ssl_cert():
    """Генерация SSL сертификата для разработки"""
    
    # Создаем директорию для сертификатов
    cert_dir = Path("ssl_certs")
    cert_dir.mkdir(exist_ok=True)
    
    # Пути к файлам сертификатов
    key_file = cert_dir / "localhost.key"
    cert_file = cert_dir / "localhost.crt"
    
    print("🔐 Генерация SSL сертификатов для разработки...")
    
    # Проверяем, есть ли уже сертификаты
    if key_file.exists() and cert_file.exists():
        print("✅ SSL сертификаты уже существуют")
        return True
    
    try:
        # Генерируем приватный ключ
        print("📝 Генерация приватного ключа...")
        subprocess.run([
            "openssl", "genrsa", "-out", str(key_file), "2048"
        ], check=True, capture_output=True)
        
        # Создаем конфигурационный файл для сертификата
        config_content = """
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = RU
ST = Moscow
L = Moscow
O = CRM Development
OU = IT Department
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
DNS.3 = 127.0.0.1
IP.1 = 127.0.0.1
"""
        
        config_file = cert_dir / "openssl.conf"
        with open(config_file, "w") as f:
            f.write(config_content)
        
        # Генерируем сертификат
        print("📜 Генерация сертификата...")
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", str(key_file),
            "-out", str(cert_file), "-days", "365", "-config", str(config_file)
        ], check=True, capture_output=True)
        
        # Удаляем конфигурационный файл
        config_file.unlink()
        
        print("✅ SSL сертификаты успешно созданы:")
        print(f"   Ключ: {key_file}")
        print(f"   Сертификат: {cert_file}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при генерации сертификатов: {e}")
        print("Убедитесь, что OpenSSL установлен в системе")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def install_cert_to_system():
    """Установка сертификата в систему (для Windows)"""
    
    if sys.platform != "win32":
        print("ℹ️ Автоматическая установка сертификатов поддерживается только в Windows")
        return
    
    cert_file = Path("ssl_certs/localhost.crt")
    
    if not cert_file.exists():
        print("❌ Сертификат не найден. Сначала сгенерируйте его.")
        return
    
    try:
        print("🔧 Установка сертификата в систему Windows...")
        
        # Копируем сертификат в хранилище сертификатов
        subprocess.run([
            "certutil", "-addstore", "-f", "ROOT", str(cert_file)
        ], check=True, capture_output=True)
        
        print("✅ Сертификат успешно установлен в систему")
        print("💡 Перезапустите браузер для применения изменений")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке сертификата: {e}")
        print("Попробуйте запустить скрипт от имени администратора")

def main():
    """Основная функция"""
    
    print("🔐 Генератор SSL сертификатов для CRM")
    print("=" * 50)
    
    # Генерируем сертификаты
    if generate_ssl_cert():
        # Предлагаем установить в систему
        if sys.platform == "win32":
            response = input("\nУстановить сертификат в систему Windows? (y/n): ")
            if response.lower() in ['y', 'yes', 'да']:
                install_cert_to_system()
    
    print("\n📋 Инструкции по использованию:")
    print("1. Для Django с SSL используйте:")
    print("   python manage.py runserver_plus --cert-file ssl_certs/localhost.crt --key-file ssl_certs/localhost.key")
    print("2. Для Nginx добавьте в конфигурацию:")
    print("   ssl_certificate ssl_certs/localhost.crt;")
    print("   ssl_certificate_key ssl_certs/localhost.key;")
    print("3. В браузере перейдите по адресу: https://localhost:8000")

if __name__ == "__main__":
    main() 