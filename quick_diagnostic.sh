#!/bin/bash

echo "🚀 Быстрая диагностика производительности CRM..."

echo ""
echo "📊 Статус контейнеров:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "⏱️ Тест скорости API Gateway:"
time curl -s http://localhost:8000/ > /dev/null

echo ""
echo "⏱️ Тест скорости User Service:"
time curl -s http://localhost:8001/ > /dev/null

echo ""
echo "⏱️ Тест скорости базы данных:"
time docker-compose exec postgres pg_isready -U crm_user

echo ""
echo "📝 Последние ошибки API Gateway:"
docker-compose logs --tail=5 api-gateway | grep -i error

echo ""
echo "📝 Последние ошибки nginx:"
docker-compose logs --tail=5 nginx | grep -i error

echo ""
echo "💾 Использование памяти:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "🔧 Проверка endpoint авторизации (должен быть быстрым):"
time curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"login":"test","password":"test"}' \
  -w "Status: %{http_code}, Time: %{time_total}s\n" || echo "❌ Ошибка" 