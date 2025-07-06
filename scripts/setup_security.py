#!/usr/bin/env python3
"""
Скрипт для автоматической настройки безопасности CRM системы
"""

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path

def generate_secret_key(length=50):
    """Генерирует безопасный SECRET_KEY"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_security_issues():
    """Проверяет критические проблемы безопасности"""
    print("🔍 Проверка безопасности...")
    
    issues = []
    
    # Проверка хардкод SECRET_KEY
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or '__pycache__' in root or 'scripts' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'django-insecure' in content:
                            issues.append(f"❌ Хардкод SECRET_KEY в {filepath}")
                except:
                    pass
    
    # Проверка .env файлов
    env_files = ['.env', '.env.local', '.env.production']
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    if 'your-secret-key' in content or 'change-this' in content:
                        issues.append(f"❌ Неизмененный SECRET_KEY в {env_file}")
            except:
                pass
    
    return issues

def setup_environment():
    """Настраивает переменные окружения"""
    print("🔧 Настройка переменных окружения...")
    
    # Создаем .env файл если его нет
    if not os.path.exists('.env'):
        print("📝 Создание .env файла...")
        
        env_content = f"""# Автоматически сгенерированные настройки безопасности
SECRET_KEY={generate_secret_key()}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=crm_production
DB_USER=crm_user
DB_PASSWORD={generate_secret_key(20)}
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# Security Settings
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Performance Settings
SLOW_REQUEST_THRESHOLD=5.0
HIGH_QUERY_COUNT_THRESHOLD=50
RATE_LIMIT_THRESHOLD=100
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env файл создан")
    else:
        print("✅ .env файл уже существует")

def setup_docker_security():
    """Настраивает безопасность Docker"""
    print("🐳 Настройка безопасности Docker...")
    
    # Проверяем docker-compose.yml
    if os.path.exists('docker-compose.yml'):
        print("✅ docker-compose.yml найден")
        
        # Проверяем наличие PostgreSQL
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
            if 'postgres' in content:
                print("✅ PostgreSQL настроен")
            else:
                print("⚠️ PostgreSQL не найден в docker-compose.yml")
    else:
        print("⚠️ docker-compose.yml не найден")

def setup_gitignore():
    """Настраивает .gitignore для безопасности"""
    print("📁 Настройка .gitignore...")
    
    security_patterns = [
        '.env',
        '.env.local',
        '.env.production',
        '*.pem',
        '*.key',
        '*.crt',
        'ssl_certs/',
        'secrets/',
        'bandit-report.json',
        'safety-report.json'
    ]
    
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern in security_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"⚠️ В .gitignore отсутствуют: {', '.join(missing_patterns)}")
        else:
            print("✅ .gitignore настроен правильно")
    else:
        print("⚠️ .gitignore не найден")

def run_security_checks():
    """Запускает проверки безопасности"""
    print("🔍 Запуск проверок безопасности...")
    
    try:
        # Проверка с bandit
        print("📊 Запуск Bandit...")
        result = subprocess.run(['bandit', '-r', '.', '-f', 'json', '-o', 'bandit-report.json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Bandit проверка завершена")
        else:
            print("⚠️ Bandit нашел проблемы безопасности")
        
        # Проверка с safety
        print("📊 Запуск Safety...")
        result = subprocess.run(['safety', 'check', '--json', '--output', 'safety-report.json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Safety проверка завершена")
        else:
            print("⚠️ Safety нашел уязвимые зависимости")
            
    except FileNotFoundError:
        print("⚠️ Bandit или Safety не установлены")
        print("Установите: pip install bandit safety")

def main():
    """Основная функция"""
    print("🔐 Настройка безопасности CRM системы")
    print("=" * 50)
    
    # Проверяем проблемы безопасности
    issues = check_security_issues()
    if issues:
        print("\n🚨 Найдены проблемы безопасности:")
        for issue in issues:
            print(f"  {issue}")
        print("\nИсправьте эти проблемы перед продолжением!")
        return 1
    
    print("✅ Критических проблем безопасности не найдено")
    
    # Настраиваем окружение
    setup_environment()
    
    # Настраиваем Docker
    setup_docker_security()
    
    # Настраиваем .gitignore
    setup_gitignore()
    
    # Запускаем проверки
    run_security_checks()
    
    print("\n" + "=" * 50)
    print("✅ Настройка безопасности завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Отредактируйте .env файл с вашими настройками")
    print("2. Запустите: docker-compose up -d")
    print("3. Проверьте логи: docker-compose logs")
    print("4. Регулярно запускайте: python scripts/setup_security.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 