#!/bin/bash

echo "🔧 Принудительно исправляем настройки базы данных в Django..."

# Остановка сервисов
echo "📦 Останавливаем сервисы..."
docker-compose stop api-gateway user-service zayavki-service finance-service

# Очистка кэша Python
echo "🧹 Очищаем кэш Python..."
docker-compose exec api-gateway find . -name "*.pyc" -delete 2>/dev/null || true
docker-compose exec user-service find . -name "*.pyc" -delete 2>/dev/null || true
docker-compose exec zayavki-service find . -name "*.pyc" -delete 2>/dev/null || true
docker-compose exec finance-service find . -name "*.pyc" -delete 2>/dev/null || true

# Проверяем настройки базы данных в каждом сервисе
echo "📋 Проверяем настройки базы данных..."

echo "API Gateway:"
docker-compose exec api-gateway python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_gateway.settings')
import django
django.setup()
from django.conf import settings
print(f'DATABASE: {settings.DATABASES[\"default\"]}')
"

echo ""
echo "User Service:"
docker-compose exec user-service python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'usersvc.settings')
import django
django.setup()
from django.conf import settings
print(f'DATABASE: {settings.DATABASES[\"default\"]}')
"

echo ""
echo "Zayavki Service:"
docker-compose exec zayavki-service python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zayavkisvc.settings')
import django
django.setup()
from django.conf import settings
print(f'DATABASE: {settings.DATABASES[\"default\"]}')
"

echo ""
echo "Finance Service:"
docker-compose exec finance-service python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financesvc.settings')
import django
django.setup()
from django.conf import settings
print(f'DATABASE: {settings.DATABASES[\"default\"]}')
"

# Запуск сервисов
echo ""
echo "🚀 Запускаем сервисы..."
docker-compose up -d api-gateway user-service zayavki-service finance-service

echo ""
echo "⏳ Ждем запуска сервисов..."
sleep 30

echo ""
echo "📊 Проверяем логи..."
docker-compose logs --tail=10

echo ""
echo "✅ Исправление завершено!" 