#!/bin/bash

echo "🔍 Проверка обновления кода..."

echo ""
echo "📊 Текущая версия файла settings.py:"
grep -n "CONN_MAX_AGE" api_gateway/api_gateway/settings.py || echo "✅ CONN_MAX_AGE не найден в глобальных переменных"

echo ""
echo "🔄 Принудительное обновление кода..."
git fetch origin
git reset --hard origin/main

echo ""
echo "📊 Проверка после обновления:"
grep -n "CONN_MAX_AGE" api_gateway/api_gateway/settings.py || echo "✅ CONN_MAX_AGE не найден в глобальных переменных"

echo ""
echo "🔍 Проверка User Service settings:"
grep -n "CONN_MAX_AGE" user_service/usersvc/settings.py || echo "✅ User Service settings в порядке"

echo ""
echo "✅ Обновление завершено!" 