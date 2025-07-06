#!/bin/bash

echo "🔍 Отладка подключения к базе данных..."

echo "📊 Проверяем переменные окружения в контейнерах:"
echo ""
echo "API Gateway:"
docker-compose exec api-gateway env | grep DB_

echo ""
echo "User Service:"
docker-compose exec user-service env | grep DB_

echo ""
echo "Zayavki Service:"
docker-compose exec zayavki-service env | grep DB_

echo ""
echo "Finance Service:"
docker-compose exec finance-service env | grep DB_

echo ""
echo "📋 Проверяем настройки Django в контейнерах:"
echo ""
echo "API Gateway settings:"
docker-compose exec api-gateway python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_gateway.settings')
django.setup()
from django.conf import settings
print(f'DB_NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'DB_USER: {settings.DATABASES[\"default\"][\"USER\"]}')
print(f'DB_HOST: {settings.DATABASES[\"default\"][\"HOST\"]}')
"

echo ""
echo "✅ Отладка завершена!" 