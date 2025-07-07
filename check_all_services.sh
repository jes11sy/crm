#!/bin/bash

echo "🔍 Полная диагностика CRM системы..."

echo ""
echo "📊 Статус Docker контейнеров:"
docker-compose ps

echo ""
echo "🔍 Проверка логов nginx:"
docker-compose logs --tail=10 nginx

echo ""
echo "🔍 Проверка логов API Gateway:"
docker-compose logs --tail=10 api-gateway

echo ""
echo "🔍 Проверка логов User Service:"
docker-compose logs --tail=10 user-service

echo ""
echo "🔍 Проверка логов Zayavki Service:"
docker-compose logs --tail=10 zayavki-service

echo ""
echo "🔍 Проверка логов Finance Service:"
docker-compose logs --tail=10 finance-service

echo ""
echo "🔍 Проверка логов Frontend:"
docker-compose logs --tail=10 frontend

echo ""
echo "🔍 Проверка базы данных:"
docker-compose exec postgres psql -U crm_user -d crm_production -c "SELECT version();" 2>/dev/null || echo "❌ Проблема с базой данных"

echo ""
echo "🔍 Проверка Redis:"
docker-compose exec redis redis-cli ping 2>/dev/null || echo "❌ Проблема с Redis"

echo ""
echo "🔍 Тест API Gateway напрямую:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/api/v1/health/ || echo "❌ API Gateway недоступен"

echo ""
echo "🔍 Тест User Service напрямую:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8001/health/ || echo "❌ User Service недоступен"

echo ""
echo "🔍 Тест Frontend напрямую:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:3000/ || echo "❌ Frontend недоступен"

echo ""
echo "🔍 Проверка портов:"
netstat -tlnp | grep -E ':(80|3000|8000|8001|8002|8003|5432|6379)' || echo "❌ Порты не открыты"

echo ""
echo "🛠️ Перезапуск всех сервисов..."
docker-compose down
docker-compose up -d

echo ""
echo "⏳ Ждем 30 секунд для запуска..."
sleep 30

echo ""
echo "📊 Статус после перезапуска:"
docker-compose ps

echo ""
echo "🔍 Финальная проверка API Gateway:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/api/v1/health/ || echo "❌ API Gateway все еще недоступен"

echo ""
echo "🔍 Финальная проверка через nginx:"
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://crm.lead-schem.ru/api/v1/health/ || echo "❌ Проблема с nginx"

echo ""
echo "✅ Диагностика завершена!" 