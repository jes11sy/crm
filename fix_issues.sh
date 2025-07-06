#!/bin/bash

echo "🔧 Исправляем текущие проблемы..."

# Остановка контейнеров
echo "📦 Останавливаем контейнеры..."
docker-compose down

# Удаление volume PostgreSQL
echo "🗄️ Удаляем старые данные PostgreSQL..."
docker volume rm crm_postgres_data 2>/dev/null || true

# Пересборка zayavki-service с новой зависимостью
echo "🔨 Пересобираем zayavki-service..."
docker-compose build --no-cache zayavki-service

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