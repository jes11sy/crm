@echo off
echo Настройка автоматического скачивания аудио от Mango Office
echo ========================================================

echo.
echo Введите настройки почты для получения аудиозаписей:
echo.

set /p MANGO_EMAIL="Email адрес (например, your-email@gmail.com): "
set /p MANGO_EMAIL_PASSWORD="Пароль от почты: "
set /p MANGO_IMAP_SERVER="IMAP сервер (по умолчанию imap.gmail.com): "
set /p MANGO_IMAP_PORT="IMAP порт (по умолчанию 993): "
set /p MANGO_DOWNLOAD_DIR="Папка для аудиофайлов (по умолчанию media/audio): "

if "%MANGO_IMAP_SERVER%"=="" set MANGO_IMAP_SERVER=imap.gmail.com
if "%MANGO_IMAP_PORT%"=="" set MANGO_IMAP_PORT=993
if "%MANGO_DOWNLOAD_DIR%"=="" set MANGO_DOWNLOAD_DIR=media/audio

echo.
echo Настройки сохранены в переменных окружения:
echo MANGO_EMAIL=%MANGO_EMAIL%
echo MANGO_EMAIL_PASSWORD=%MANGO_EMAIL_PASSWORD%
echo MANGO_IMAP_SERVER=%MANGO_IMAP_SERVER%
echo MANGO_IMAP_PORT=%MANGO_IMAP_PORT%
echo MANGO_DOWNLOAD_DIR=%MANGO_DOWNLOAD_DIR%

echo.
echo Теперь запустите Django сервер с этими переменными:
echo set MANGO_EMAIL=%MANGO_EMAIL% && set MANGO_EMAIL_PASSWORD=%MANGO_EMAIL_PASSWORD% && set MANGO_IMAP_SERVER=%MANGO_IMAP_SERVER% && set MANGO_IMAP_PORT=%MANGO_IMAP_PORT% && set MANGO_DOWNLOAD_DIR=%MANGO_DOWNLOAD_DIR% && python manage.py runserver

echo.
echo Или добавьте эти переменные в системные переменные окружения Windows
echo для постоянного использования.
echo.
pause 