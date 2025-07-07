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
docker-compose logs --tail=20 api-gateway

echo ""
echo "🔧 Тест API Gateway:"
timeout 5 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/api/v1/health/ || echo "❌ API Gateway недоступен"

echo ""
echo "🔧 Тест авторизации:"
timeout 5 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" -X POST http://localhost:8000/api/v1/auth/login/ -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass"}' || echo "❌ Ошибка авторизации"

echo ""
echo "🔍 Проверка базы данных:"
docker-compose exec postgres psql -U crm_user -d crm_production -c "SELECT version();" 2>/dev/null || echo "❌ Проблема с подключением к базе"

echo ""
echo "🔍 Проверка Redis:"
docker-compose exec redis redis-cli ping 2>/dev/null || echo "❌ Проблема с Redis"

echo ""
echo "🔍 Проверка User Service:"
docker-compose logs --tail=10 user-service

echo ""
echo "✅ Исправление завершено!"
echo ""
echo "💡 Если проблемы остались, попробуйте:"
echo "   docker-compose down"
echo "   docker-compose up -d" 