#!/bin/bash

echo "🔍 Проверяем состояние базы данных..."

# Подключаемся к PostgreSQL и проверяем базы данных
echo "📊 Список баз данных:"
docker-compose exec postgres psql -U crm_user -l

echo ""
echo "🔧 Создаем базу данных crm_production если её нет:"
docker-compose exec postgres psql -U crm_user -c "CREATE DATABASE crm_production;" 2>/dev/null || echo "База данных уже существует"

echo ""
echo "📋 Проверяем подключение к базе данных:"
docker-compose exec postgres psql -U crm_user -d crm_production -c "SELECT version();"

echo ""
echo "✅ Проверка завершена!" 