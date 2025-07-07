#!/bin/bash

echo "🔍 Диагностика CRM системы..."

echo ""
echo "📊 Статус Docker контейнеров:"
docker-compose ps

echo ""
echo "🌐 Проверка доступности сервисов:"
echo "API Gateway:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/ || echo "❌ API Gateway недоступен"

echo "User Service:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8001/ || echo "❌ User Service недоступен"

echo "Zayavki Service:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8002/ || echo "❌ Zayavki Service недоступен"

echo "Finance Service:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8003/ || echo "❌ Finance Service недоступен"

echo "Frontend:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:3000/ || echo "❌ Frontend недоступен"

echo ""
echo "🗄️ Проверка базы данных:"
docker-compose exec postgres pg_isready -U crm_user || echo "❌ База данных недоступна"

echo ""
echo "📝 Последние логи API Gateway:"
docker-compose logs --tail=10 api-gateway

echo ""
echo "📝 Последние логи User Service:"
docker-compose logs --tail=10 user-service

echo ""
echo "📝 Последние логи nginx:"
docker-compose logs --tail=10 nginx

echo ""
echo "🔧 Проверка endpoint авторизации:"
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}' \
  -w "Status: %{http_code}, Time: %{time_total}s\n" || echo "❌ Ошибка при тестировании авторизации" 