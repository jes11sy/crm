#!/bin/bash

echo "⚡ Быстрый перезапуск CRM с оптимизациями..."

# Останавливаем контейнеры
echo "⏹️ Останавливаем контейнеры..."
docker-compose down

# Очищаем кэш Docker
echo "🧹 Очищаем кэш..."
docker system prune -f

# Пересобираем и запускаем
echo "🔨 Пересобираем и запускаем..."
docker-compose up --build -d

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 20

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose ps

# Тестируем скорость
echo "⚡ Тест скорости:"
time curl -s http://localhost:8000/ > /dev/null

echo "✅ Перезапуск завершен!"
echo "🌐 Frontend: http://crm.lead-schem.ru/"
echo "🔧 API: http://crm.lead-schem.ru/api/" 