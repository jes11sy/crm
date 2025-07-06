@echo off
set DOMAIN=%1
set SUBDOMAIN=crm
set FULL_DOMAIN=%SUBDOMAIN%.%DOMAIN%

echo Обновление SSL сертификатов для %FULL_DOMAIN%...

REM Обновление сертификатов
docker-compose -f docker-compose-production.yml run --rm certbot renew

REM Перезагрузка nginx
docker-compose -f docker-compose-production.yml restart nginx

echo SSL сертификаты обновлены
