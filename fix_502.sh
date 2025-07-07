#!/bin/bash

echo "🚨 Исправление ошибки 502 Bad Gateway..."

echo ""
echo "📊 Текущий статус:"
docker-compose ps

echo ""
echo "🔍 Проверка логов nginx:"
docker-compose logs --tail=5 nginx

echo ""
echo "🔍 Проверка логов API Gateway:"
docker-compose logs --tail=5 api-gateway

echo ""
echo "🛑 Останавливаем все сервисы..."
docker-compose down

echo ""
echo "🧹 Очищаем неиспользуемые контейнеры..."
docker system prune -f

echo ""
echo "🚀 Запускаем сервисы заново..."
docker-compose up -d

echo ""
echo "⏳ Ждем 20 секунд для запуска..."
sleep 20

echo ""
echo "📊 Статус после перезапуска:"
docker-compose ps

echo ""
echo "🔍 Проверка API Gateway:"
timeout 10 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/api/v1/health/ || echo "❌ API Gateway недоступен"

echo ""
echo "🔍 Проверка через nginx:"
timeout 10 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://crm.lead-schem.ru/api/v1/health/ || echo "❌ Проблема с nginx"

echo ""
echo "🔍 Проверка авторизации:"
timeout 10 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" -X POST http://crm.lead-schem.ru/api/v1/auth/login/ -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass"}' || echo "❌ Ошибка авторизации"

echo ""
echo "✅ Исправление завершено!"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Система должна работать! Попробуйте зайти на http://crm.lead-schem.ru"
else
    echo ""
    echo "⚠️ Возможны проблемы. Запустите полную диагностику:"
    echo "   bash check_all_services.sh"
fi 