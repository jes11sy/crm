#!/bin/bash

echo "🔧 Быстрое исправление проблем..."

echo ""
echo "📊 Текущий статус:"
docker-compose ps

echo ""
echo "🛑 Перезапускаем только API Gateway..."
docker-compose restart api-gateway

echo ""
echo "⏳ Ждем 10 секунд..."
sleep 10

echo ""
echo "📝 Логи API Gateway:"
docker-compose logs --tail=5 api-gateway

echo ""
echo "🔧 Тест API Gateway:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/ || echo "❌ API Gateway недоступен"

echo ""
echo "🔧 Тест авторизации:"
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"login":"test","password":"test"}' \
  -w "Status: %{http_code}, Time: %{time_total}s\n" || echo "❌ Ошибка авторизации"

echo ""
echo "✅ Исправление завершено!" 