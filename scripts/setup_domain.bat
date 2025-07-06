@echo off
setlocal enabledelayedexpansion

REM Скрипт настройки домена для CRM системы (Windows)
REM Использование: setup_domain.bat yourdomain.com

if "%~1"=="" (
    echo ERROR: Необходимо указать домен!
    echo Использование: %0 yourdomain.com
    exit /b 1
)

set DOMAIN=%~1
set SUBDOMAIN=crm
set FULL_DOMAIN=%SUBDOMAIN%.%DOMAIN%

echo [%date% %time%] Начинаем настройку домена: %FULL_DOMAIN%

REM Проверка наличия необходимых файлов
if not exist "docker-compose-production.yml" (
    echo ERROR: Файл docker-compose-production.yml не найден!
    exit /b 1
)

if not exist "nginx-production.conf" (
    echo ERROR: Файл nginx-production.conf не найден!
    exit /b 1
)

REM Создание директорий
echo [%date% %time%] Создание необходимых директорий...
if not exist "ssl_certs" mkdir ssl_certs
if not exist "certbot_webroot" mkdir certbot_webroot
if not exist "logs" mkdir logs

REM Обновление конфигурационных файлов
echo [%date% %time%] Обновление конфигурационных файлов...

REM Обновление nginx конфигурации
powershell -Command "(Get-Content nginx-production.conf) -replace 'crm\.yourdomain\.com', '%FULL_DOMAIN%' | Set-Content nginx-production.conf"
powershell -Command "(Get-Content nginx-production.conf) -replace 'www\.crm\.yourdomain\.com', 'www.%FULL_DOMAIN%' | Set-Content nginx-production.conf"

REM Обновление docker-compose
powershell -Command "(Get-Content docker-compose-production.yml) -replace 'crm\.yourdomain\.com', '%FULL_DOMAIN%' | Set-Content docker-compose-production.yml"
powershell -Command "(Get-Content docker-compose-production.yml) -replace 'www\.crm\.yourdomain\.com', 'www.%FULL_DOMAIN%' | Set-Content docker-compose-production.yml"

REM Создание .env файла для production
echo [%date% %time%] Создание .env файла для production...

REM Генерация случайных паролей
for /f %%i in ('powershell -Command "Add-Type -AssemblyName System.Security; [System.Web.Security.Membership]::GeneratePassword(32, 10)"') do set DB_PASSWORD=%%i
for /f %%i in ('powershell -Command "Add-Type -AssemblyName System.Security; [System.Web.Security.Membership]::GeneratePassword(64, 15)"') do set SECRET_KEY=%%i

(
echo # Database settings
echo DB_NAME=crm_production
echo DB_USER=crm_user
echo DB_PASSWORD=%DB_PASSWORD%
echo.
echo # Django settings
echo SECRET_KEY=%SECRET_KEY%
echo DEBUG=False
echo.
echo # Domain settings
echo DOMAIN=%FULL_DOMAIN%
echo ALLOWED_HOSTS=%FULL_DOMAIN%,www.%FULL_DOMAIN%
echo.
echo # SSL settings
echo SSL_EMAIL=admin@%DOMAIN%
echo.
echo # Redis settings
echo REDIS_URL=redis://redis:6379/0
echo.
echo # Email settings ^(настройте под ваши нужды^)
echo EMAIL_HOST=smtp.gmail.com
echo EMAIL_PORT=587
echo EMAIL_USE_TLS=True
echo EMAIL_HOST_USER=your-email@gmail.com
echo EMAIL_HOST_PASSWORD=your-app-password
echo.
echo # Mango Office settings ^(если используется^)
echo MANGO_OFFICE_API_KEY=your-mango-api-key
echo MANGO_OFFICE_API_URL=https://app.mango-office.ru/vpbx/
echo.
echo # Telegram settings ^(если используется^)
echo TELEGRAM_BOT_TOKEN=your-telegram-bot-token
echo TELEGRAM_CHAT_ID=your-telegram-chat-id
) > .env.production

echo [%date% %time%] .env.production файл создан

REM Создание скрипта для получения SSL сертификатов
echo [%date% %time%] Создание скрипта для SSL сертификатов...
(
echo @echo off
echo set DOMAIN=%%1
echo set SUBDOMAIN=crm
echo set FULL_DOMAIN=%%SUBDOMAIN%%.%%DOMAIN%%
echo.
echo echo Получение SSL сертификатов для %%FULL_DOMAIN%%...
echo.
echo REM Остановка nginx для освобождения порта 80
echo docker-compose -f docker-compose-production.yml stop nginx
echo.
echo REM Получение сертификатов
echo docker-compose -f docker-compose-production.yml --profile ssl-setup run --rm certbot
echo.
echo REM Запуск nginx
echo docker-compose -f docker-compose-production.yml up -d nginx
echo.
echo echo SSL сертификаты получены!
) > scripts\get_ssl_cert.bat

REM Создание скрипта для обновления SSL сертификатов
echo [%date% %time%] Создание скрипта для обновления SSL сертификатов...
(
echo @echo off
echo set DOMAIN=%%1
echo set SUBDOMAIN=crm
echo set FULL_DOMAIN=%%SUBDOMAIN%%.%%DOMAIN%%
echo.
echo echo Обновление SSL сертификатов для %%FULL_DOMAIN%%...
echo.
echo REM Обновление сертификатов
echo docker-compose -f docker-compose-production.yml run --rm certbot renew
echo.
echo REM Перезагрузка nginx
echo docker-compose -f docker-compose-production.yml restart nginx
echo.
echo echo SSL сертификаты обновлены!
) > scripts\renew_ssl.bat

REM Создание скрипта для мониторинга
echo [%date% %time%] Создание скрипта мониторинга...
(
echo @echo off
echo set DOMAIN=%%1
echo set SUBDOMAIN=crm
echo set FULL_DOMAIN=%%SUBDOMAIN%%.%%DOMAIN%%
echo.
echo echo Мониторинг системы CRM...
echo.
echo REM Проверка доступности сайта
echo curl -f -s "https://%%FULL_DOMAIN%%/health" ^>nul 2^>^&1
echo if %%errorlevel%% equ 0 ^(
echo     echo ✅ Сайт доступен
echo ^) else ^(
echo     echo ❌ Сайт недоступен
echo ^)
echo.
echo REM Проверка Docker
echo docker info ^>nul 2^>^&1
echo if %%errorlevel%% equ 0 ^(
echo     echo ✅ Docker работает
echo ^) else ^(
echo     echo ❌ Docker не запущен
echo ^)
echo.
echo REM Проверка файлов
echo if exist "docker-compose-production.yml" ^(
echo     echo ✅ docker-compose-production.yml найден
echo ^) else ^(
echo     echo ❌ docker-compose-production.yml не найден
echo ^)
echo.
echo if exist "nginx-production.conf" ^(
echo     echo ✅ nginx-production.conf найден
echo ^) else ^(
echo     echo ❌ nginx-production.conf не найден
echo ^)
echo.
echo if exist ".env.production" ^(
echo     echo ✅ .env.production найден
echo ^) else ^(
echo     echo ❌ .env.production не найден
echo ^)
) > scripts\monitor.bat

REM Создание инструкции по настройке DNS
echo [%date% %time%] Создание инструкции по настройке DNS...
(
echo # Настройка DNS для домена %FULL_DOMAIN%
echo.
echo ## Необходимые DNS записи:
echo.
echo ### A записи:
echo - `%SUBDOMAIN%.%DOMAIN%` → IP адрес вашего сервера
echo - `www.%SUBDOMAIN%.%DOMAIN%` → IP адрес вашего сервера
echo.
echo ### CNAME записи ^(опционально^):
echo - `www.%SUBDOMAIN%.%DOMAIN%` → `%SUBDOMAIN%.%DOMAIN%`
echo.
echo ## Пример для популярных регистраторов:
echo.
echo ### Cloudflare:
echo 1. Добавьте домен в Cloudflare
echo 2. Создайте A запись: `%SUBDOMAIN%` → IP сервера
echo 3. Включите SSL/TLS в режиме "Full ^(strict^)"
echo.
echo ### REG.RU:
echo 1. Войдите в панель управления
echo 2. Перейдите в "DNS записи"
echo 3. Добавьте A запись: `%SUBDOMAIN%` → IP сервера
echo.
echo ### Namecheap:
echo 1. Войдите в аккаунт
echo 2. Перейдите в "Domain List" → "Manage"
echo 3. В разделе "Advanced DNS" добавьте A запись: `%SUBDOMAIN%` → IP сервера
echo.
echo ## Проверка настройки:
echo ```bash
echo # Проверка DNS записи
echo nslookup %FULL_DOMAIN%
echo.
echo # Проверка доступности
echo curl -I http://%FULL_DOMAIN%
echo ```
echo.
echo ## Важные замечания:
echo - DNS изменения могут распространяться до 24 часов
echo - Убедитесь, что порты 80 и 443 открыты на сервере
echo - Проверьте настройки файрвола
) > DNS_SETUP.md

REM Создание скрипта для проверки готовности
echo [%date% %time%] Создание скрипта проверки готовности...
(
echo @echo off
echo set DOMAIN=%%1
echo set SUBDOMAIN=crm
echo set FULL_DOMAIN=%%SUBDOMAIN%%.%%DOMAIN%%
echo.
echo echo Проверка готовности системы...
echo.
echo REM Проверка DNS
echo echo Проверка DNS записи...
echo nslookup %%FULL_DOMAIN%% ^>nul 2^>^&1
echo if %%errorlevel%% equ 0 ^(
echo     echo ✅ DNS запись настроена
echo ^) else ^(
echo     echo ❌ DNS запись не найдена
echo     echo Настройте A запись: %%SUBDOMAIN%% → IP вашего сервера
echo ^)
echo.
echo REM Проверка Docker
echo echo Проверка Docker...
echo docker info ^>nul 2^>^&1
echo if %%errorlevel%% equ 0 ^(
echo     echo ✅ Docker работает
echo ^) else ^(
echo     echo ❌ Docker не запущен
echo ^)
echo.
echo REM Проверка файлов
echo echo Проверка конфигурационных файлов...
echo if exist "docker-compose-production.yml" ^(
echo     echo ✅ docker-compose-production.yml найден
echo ^) else ^(
echo     echo ❌ docker-compose-production.yml не найден
echo ^)
echo.
echo if exist "nginx-production.conf" ^(
echo     echo ✅ nginx-production.conf найден
echo ^) else ^(
echo     echo ❌ nginx-production.conf не найден
echo ^)
echo.
echo if exist ".env.production" ^(
echo     echo ✅ .env.production найден
echo ^) else ^(
echo     echo ❌ .env.production не найден
echo ^)
echo.
echo echo.
echo echo Для запуска системы выполните:
echo echo docker-compose -f docker-compose-production.yml --env-file .env.production up -d
echo echo.
echo echo Для получения SSL сертификатов выполните:
echo echo scripts\get_ssl_cert.bat %%DOMAIN%%
) > scripts\check_readiness.bat

REM Создание финальной инструкции
echo [%date% %time%] Создание финальной инструкции...
(
echo # Руководство по развертыванию CRM системы на домене %FULL_DOMAIN%
echo.
echo ## Шаги для развертывания:
echo.
echo ### 1. Подготовка сервера
echo - Убедитесь, что у вас есть VPS/сервер с Ubuntu 20.04+
echo - Установите Docker и Docker Compose
echo - Откройте порты 80 и 443
echo.
echo ### 2. Настройка DNS
echo Следуйте инструкции в файле `DNS_SETUP.md`
echo.
echo ### 3. Загрузка проекта
echo ```bash
echo git clone ^<your-repo-url^>
echo cd crm-system
echo ```
echo.
echo ### 4. Настройка домена
echo ```bash
echo scripts\setup_domain.bat %DOMAIN%
echo ```
echo.
echo ### 5. Проверка готовности
echo ```bash
echo scripts\check_readiness.bat %DOMAIN%
echo ```
echo.
echo ### 6. Запуск системы
echo ```bash
echo docker-compose -f docker-compose-production.yml --env-file .env.production up -d
echo ```
echo.
echo ### 7. Получение SSL сертификатов
echo ```bash
echo scripts\get_ssl_cert.bat %DOMAIN%
echo ```
echo.
echo ### 8. Проверка работы
echo Откройте в браузере: https://%FULL_DOMAIN%
echo.
echo ## Полезные команды:
echo.
echo ### Просмотр логов:
echo ```bash
echo docker-compose -f docker-compose-production.yml logs -f
echo ```
echo.
echo ### Остановка системы:
echo ```bash
echo docker-compose -f docker-compose-production.yml down
echo ```
echo.
echo ### Обновление системы:
echo ```bash
echo git pull
echo docker-compose -f docker-compose-production.yml build
echo docker-compose -f docker-compose-production.yml up -d
echo ```
echo.
echo ### Мониторинг:
echo ```bash
echo scripts\monitor.bat %DOMAIN%
echo ```
echo.
echo ## Контакты поддержки:
echo - Email: support@%DOMAIN%
echo - Документация: https://%FULL_DOMAIN%/docs
) > DEPLOYMENT_GUIDE.md

echo [%date% %time%] Настройка домена завершена!
echo.
echo INFO: Следующие шаги:
echo 1. Настройте DNS записи ^(см. DNS_SETUP.md^)
echo 2. Проверьте готовность: scripts\check_readiness.bat %DOMAIN%
echo 3. Запустите систему: docker-compose -f docker-compose-production.yml --env-file .env.production up -d
echo 4. Получите SSL сертификаты: scripts\get_ssl_cert.bat %DOMAIN%
echo.
echo INFO: Документация создана в файле DEPLOYMENT_GUIDE.md 