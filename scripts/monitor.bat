@echo off
set DOMAIN=%1
set SUBDOMAIN=crm
set FULL_DOMAIN=%SUBDOMAIN%.%DOMAIN%

echo Мониторинг системы CRM...

REM Проверка доступности сайта
curl -f -s "https://%FULL_DOMAIN%/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Сайт доступен
) else (
    echo ❌ Сайт недоступен
)

REM Проверка Docker
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker работает
) else (
    echo ❌ Docker не запущен
)

REM Проверка файлов
if exist "docker-compose-production.yml" (
    echo ✅ docker-compose-production.yml найден
) else (
    echo ❌ docker-compose-production.yml не найден
)

if exist "nginx-production.conf" (
    echo ✅ nginx-production.conf найден
) else (
    echo ❌ nginx-production.conf не найден
)

if exist ".env.production" (
    echo ✅ .env.production найден
) else (
    echo ❌ .env.production не найден
)
