@echo off
echo Запуск мониторинга почты Mango Office
echo =====================================

echo.
echo Настройка переменных окружения...

set MANGO_EMAIL=recordmango1@rambler.ru
set MANGO_EMAIL_PASSWORD=iV6cdwmdln3bx0xx
set MANGO_IMAP_SERVER=imap.rambler.ru
set MANGO_IMAP_PORT=993
set MANGO_DOWNLOAD_DIR=media/audio

echo Email: %MANGO_EMAIL%
echo IMAP: %MANGO_IMAP_SERVER%:%MANGO_IMAP_PORT%
echo Папка: %MANGO_DOWNLOAD_DIR%

echo.
echo Запуск мониторинга...
echo Нажмите Ctrl+C для остановки
echo.

python mango_email_monitor.py

pause 