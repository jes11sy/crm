@echo off
set DOMAIN=%1
set SUBDOMAIN=crm
set FULL_DOMAIN=%SUBDOMAIN%.%DOMAIN%

echo Получение SSL сертификатов для %FULL_DOMAIN%...

REM Остановка nginx для освобождения порта 80
docker-compose -f docker-compose-production.yml stop nginx

REM Получение сертификатов
docker-compose -f docker-compose-production.yml --profile ssl-setup run --rm certbot

REM Запуск nginx
docker-compose -f docker-compose-production.yml up -d nginx

echo SSL сертификаты получены
