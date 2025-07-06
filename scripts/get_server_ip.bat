@echo off
chcp 65001 >nul
echo [%date% %time%] Определение IP адреса сервера...

REM Получаем внешний IP адрес
for /f "tokens=*" %%i in ('curl -s ifconfig.me 2^>nul') do set EXTERNAL_IP=%%i

REM Получаем локальный IP адрес
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    set LOCAL_IP=%%i
    set LOCAL_IP=!LOCAL_IP: =!
    goto :found_local
)

:found_local

echo.
echo ========================================
echo IP АДРЕСА СЕРВЕРА:
echo ========================================
echo Внешний IP: %EXTERNAL_IP%
echo Локальный IP: %LOCAL_IP%
echo.

REM Создаем файл с IP адресами
echo # IP адреса сервера > SERVER_IPS.txt
echo Внешний IP: %EXTERNAL_IP% >> SERVER_IPS.txt
echo Локальный IP: %LOCAL_IP% >> SERVER_IPS.txt
echo. >> SERVER_IPS.txt
echo Для настройки DNS используйте ВНЕШНИЙ IP: %EXTERNAL_IP% >> SERVER_IPS.txt

echo [%date% %time%] IP адреса сохранены в файл SERVER_IPS.txt
echo.
echo ========================================
echo ИНСТРУКЦИЯ ПО НАСТРОЙКЕ DNS:
echo ========================================
echo 1. Войдите в панель управления Timeweb
echo 2. Найдите домен lead-schem.ru
echo 3. Перейдите в раздел "DNS-записи"
echo 4. Добавьте A запись:
echo    - Имя: crm
echo    - Значение: %EXTERNAL_IP%
echo 5. Добавьте A запись:
echo    - Имя: www.crm
echo    - Значение: %EXTERNAL_IP%
echo.
echo После настройки DNS подождите 30-60 минут
echo и выполните: scripts\check_readiness.bat lead-schem.ru
echo.
pause 