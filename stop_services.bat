@echo off
echo Stopping CRM Microservices Architecture...
echo.

echo Stopping all Python processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

echo.
echo All services stopped.
echo.
pause 