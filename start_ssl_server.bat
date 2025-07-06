@echo off
chcp 65001 >nul
echo 🔐 Запуск CRM с SSL поддержкой
echo ================================================

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден. Установите Python и добавьте в PATH
    pause
    exit /b 1
)

REM Проверяем наличие OpenSSL
openssl version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ OpenSSL не найден. Установите OpenSSL для генерации сертификатов
    echo Скачать: https://slproweb.com/products/Win32OpenSSL.html
    pause
)

REM Генерируем SSL сертификаты если их нет
if not exist "ssl_certs\localhost.crt" (
    echo 📜 Генерация SSL сертификатов...
    python scripts\generate_ssl_cert.py
    if errorlevel 1 (
        echo ❌ Ошибка при генерации сертификатов
        pause
        exit /b 1
    )
)

REM Устанавливаем django-extensions
echo 📦 Проверка django-extensions...
python -c "import django_extensions" >nul 2>&1
if errorlevel 1 (
    echo 📦 Установка django-extensions...
    pip install django-extensions
    if errorlevel 1 (
        echo ❌ Ошибка при установке django-extensions
        pause
        exit /b 1
    )
)

REM Добавляем django_extensions в INSTALLED_APPS если его нет
echo 🔧 Настройка Django...
findstr "django_extensions" panel\settings.py >nul
if errorlevel 1 (
    echo 🔧 Добавление django_extensions в настройки...
    powershell -Command "(Get-Content panel\settings.py) -replace 'INSTALLED_APPS = \[', 'INSTALLED_APPS = [\n    ''django_extensions'',' | Set-Content panel\settings.py"
)

REM Запускаем сервер с SSL
echo 🚀 Запуск Django сервера с SSL...
echo 💡 Откройте: https://localhost:8000
echo 💡 Для остановки нажмите Ctrl+C
echo ================================================

python manage.py runserver_plus --cert-file ssl_certs\localhost.crt --key-file ssl_certs\localhost.key --addrport 0.0.0.0:8000

echo.
echo 👋 Сервер остановлен
pause 