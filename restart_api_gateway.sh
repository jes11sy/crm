#!/bin/bash

echo "🔄 Пересборка и перезапуск API Gateway..."

# Остановка API Gateway
echo "📦 Останавливаем API Gateway..."
docker-compose stop api-gateway

# Удаление образа API Gateway
echo "🗑️ Удаляем старый образ API Gateway..."
docker-compose rm -f api-gateway

# Пересборка API Gateway
echo "🔨 Пересобираем API Gateway..."
docker-compose build --no-cache api-gateway

# Запуск API Gateway
echo "🚀 Запускаем API Gateway..."
docker-compose up -d api-gateway

# Ожидание запуска
echo "⏳ Ждем запуска API Gateway..."
sleep 10

# Проверка статуса
echo "📊 Проверяем статус..."
docker-compose ps api-gateway

# Проверка логов
echo "📋 Проверяем логи..."
docker-compose logs --tail=5 api-gateway

echo "✅ Перезапуск завершен!" 