@echo off
set DOMAIN=%1
set SUBDOMAIN=crm
set FULL_DOMAIN=%SUBDOMAIN%.%DOMAIN%

echo Проверка готовности системы...

REM Проверка DNS
echo Проверка DNS записи...
nslookup %FULL_DOMAIN% >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ DNS запись настроена
) else (
    echo ❌ DNS запись не найдена
    echo Настройте A запись: %SUBDOMAIN% → IP вашего сервера
)

REM Проверка Docker
echo Проверка Docker...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker работает
) else (
    echo ❌ Docker не запущен
)

REM Проверка файлов
echo Проверка конфигурационных файлов...
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

echo.
echo Для запуска системы выполните:
echo docker-compose -f docker-compose-production.yml --env-file .env.production up -d
echo.
echo Для получения SSL сертификатов выполните:
echo scripts\get_ssl_cert.bat %DOMAIN%
