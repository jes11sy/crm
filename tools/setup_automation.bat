@echo off
echo Настройка автоматической обработки писем Mango Office
echo.

REM Создаем задачу в планировщике Windows
schtasks /create /tn "MangoEmailProcessing" /tr "cmd /c cd /d C:\Users\МАРТА\Desktop\дубль 2 && python manage.py process_mango_emails --email recordmango1@rambler.ru --password iV6cdwmdln3bx0xx --imap-server imap.rambler.ru --imap-port 993" /sc minute /mo 5 /ru "SYSTEM" /f

echo.
echo Задача создана! Обработка писем будет запускаться каждые 5 минут.
echo.
echo Для проверки статуса: schtasks /query /tn "MangoEmailProcessing"
echo Для удаления задачи: schtasks /delete /tn "MangoEmailProcessing" /f
echo.
pause 