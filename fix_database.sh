#!/bin/bash

echo "🔧 Исправляем проблемы с базой данных и namespace..."

# Остановка контейнеров
echo "📦 Останавливаем контейнеры..."
docker-compose down

# Удаление volume PostgreSQL для пересоздания
echo "🗄️ Удаляем старые данные PostgreSQL..."
docker volume rm crm_postgres_data 2>/dev/null || true

# Пересборка api-gateway (удален дублирующий urls.py)
echo "🔨 Пересобираем api-gateway..."
docker-compose build --no-cache api-gateway

# Запуск сервисов
echo "🚀 Запускаем сервисы..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Ждем запуска сервисов..."
sleep 30

# Проверка статуса
echo "📊 Проверяем статус сервисов..."
docker-compose ps

echo "✅ Исправления применены!"
echo "📋 Проверьте логи: docker-compose logs -f" 