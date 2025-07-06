#!/bin/bash

echo "🔄 Перезапуск CRM системы с frontend..."

# Останавливаем все контейнеры
echo "⏹️  Останавливаем контейнеры..."
docker-compose down

# Удаляем старые образы frontend
echo "🧹 Очищаем старые образы frontend..."
docker rmi $(docker images -q crm-frontend) 2>/dev/null || true

# Пересобираем и запускаем все сервисы
echo "🔨 Пересобираем и запускаем сервисы..."
docker-compose up --build -d

# Ждем запуска сервисов
echo "⏳ Ждем запуска сервисов..."
sleep 30

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose ps

echo "✅ Перезапуск завершен!"
echo "🌐 Frontend должен быть доступен по адресу: http://crm.lead-schem.ru/"
echo "🔧 API доступен по адресу: http://crm.lead-schem.ru/api/" 