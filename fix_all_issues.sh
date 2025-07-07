#!/bin/bash

echo "🚨 Исправление всех проблем CRM системы..."

echo ""
echo "📊 Текущий статус:"
docker-compose ps

echo ""
echo "🔄 Обновление кода..."
git fetch origin
git reset --hard origin/main

echo ""
echo "🔍 Проверка исправлений в коде..."
echo "API Gateway settings:"
grep -n "CONN_MAX_AGE" api_gateway/api_gateway/settings.py || echo "✅ CONN_MAX_AGE исправлен"

echo ""
echo "User Service Dockerfile:"
grep -n "usersvc.wsgi" user_service/Dockerfile || echo "✅ User Service Dockerfile исправлен"

echo ""
echo "🛑 Останавливаем все сервисы..."
docker-compose down

echo ""
echo "🧹 Очищаем образы..."
docker system prune -f

echo ""
echo "🔨 Пересобираем контейнеры..."
docker-compose build --no-cache

echo ""
echo "🚀 Запускаем сервисы..."
docker-compose up -d

echo ""
echo "⏳ Ждем 40 секунд для полного запуска..."
sleep 40

echo ""
echo "📊 Статус после исправлений:"
docker-compose ps

echo ""
echo "🔍 Проверка API Gateway:"
timeout 10 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8000/api/v1/health/ || echo "❌ API Gateway недоступен"

echo ""
echo "🔍 Проверка User Service:"
timeout 10 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://localhost:8001/health/ || echo "❌ User Service недоступен"

echo ""
echo "🔍 Проверка через nginx:"
timeout 10 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" http://crm.lead-schem.ru/api/v1/health/ || echo "❌ Проблема с nginx"

echo ""
echo "🔍 Проверка авторизации:"
timeout 10 curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s\n" -X POST http://crm.lead-schem.ru/api/v1/auth/login/ -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass"}' || echo "❌ Ошибка авторизации"

echo ""
echo "📝 Логи API Gateway:"
docker-compose logs --tail=5 api-gateway

echo ""
echo "📝 Логи User Service:"
docker-compose logs --tail=5 user-service

echo ""
echo "✅ Исправления завершены!"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Система должна работать! Попробуйте зайти на http://crm.lead-schem.ru"
else
    echo ""
    echo "⚠️ Возможны проблемы. Проверьте логи:"
    echo "   docker-compose logs api-gateway"
    echo "   docker-compose logs user-service"
fi 