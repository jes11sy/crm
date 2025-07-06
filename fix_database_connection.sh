#!/bin/bash

echo "🔧 Исправляем подключение к базе данных..."

# Подключаемся к системной базе данных postgres
echo "📊 Подключаемся к системной базе данных..."
docker-compose exec postgres psql -U crm_user -d postgres -c "SELECT datname FROM pg_database;"

echo ""
echo "🔧 Создаем базу данных crm_production..."
docker-compose exec postgres psql -U crm_user -d postgres -c "CREATE DATABASE crm_production;" 2>/dev/null || echo "База данных уже существует"

echo ""
echo "📋 Проверяем подключение к новой базе данных..."
docker-compose exec postgres psql -U crm_user -d crm_production -c "SELECT version();"

echo ""
echo "✅ Исправление завершено!" 