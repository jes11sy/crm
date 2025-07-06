# 📝 Настройка логирования с поддержкой UTF-8 для Windows

## 🎯 Обзор

Данная документация описывает настройку системы логирования CRM с поддержкой UTF-8 кодировки для корректной работы на Windows.

## 🚨 Проблема

На Windows системах возникала ошибка при логировании сообщений с эмодзи:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f510' in position 81
```

## ✅ Решение

### 1. Кастомные хендлеры логирования

Созданы специальные хендлеры в `core/logging_handlers.py`:

#### SafeUTF8FileHandler
- Безопасно обрабатывает эмодзи в лог-файлах
- Заменяет проблемные символы на текстовые эквиваленты
- Использует UTF-8 кодировку

#### ConsoleHandler
- Обрабатывает вывод в консоль
- Настраивает кодировку для Windows
- Безопасно отображает эмодзи

### 2. Настройка в settings.py

```python
# Настройка логирования для Windows
try:
    from core.logging_handlers import setup_windows_logging
    setup_windows_logging()
except ImportError:
    pass

# Конфигурация логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'core.logging_handlers.SafeUTF8FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'alerts_file': {
            'level': 'WARNING',
            'class': 'core.logging_handlers.SafeUTF8FileHandler',
            'filename': BASE_DIR / 'logs' / 'alerts.log',
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'INFO',
            'class': 'core.logging_handlers.ConsoleHandler',
            'formatter': 'verbose',
        },
        'telegram': {
            'level': 'ERROR',
            'class': 'core.telegram_handler.TelegramLogHandler',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

## 🔧 Замена эмодзи

Система автоматически заменяет эмодзи на безопасные текстовые эквиваленты:

| Эмодзи | Замена | Описание |
|--------|--------|----------|
| 🔐 | [LOGIN] | Вход в систему |
| ⏰ | [TIME] | Время |
| 📄 | [DESC] | Описание |
| 👤 | [USER] | Пользователь |
| 🚨 | [ERROR] | Ошибка |
| ⚠️ | [WARNING] | Предупреждение |
| ✅ | [SUCCESS] | Успех |
| ❌ | [FAIL] | Неудача |
| 💰 | [MONEY] | Деньги |
| 📝 | [NOTE] | Заметка |
| 🔗 | [LINK] | Ссылка |
| 📋 | [DETAILS] | Детали |
| ℹ️ | [INFO] | Информация |
| 📢 | [ALERT] | Уведомление |

## 🧪 Тестирование

Для тестирования логирования используйте скрипт:

```bash
python scripts/test_logging.py
```

Скрипт проверит:
- ✅ Логирование в файлы
- ✅ Отправку Telegram уведомлений
- ✅ Обработку эмодзи
- ✅ Создание лог-файлов

## 📁 Структура лог-файлов

```
logs/
├── django.log      # Основные логи приложения
├── alerts.log      # Логи предупреждений и ошибок
├── mango_import.log # Логи импорта Mango
└── auto_import_mango.log # Логи автоматического импорта
```

## 🔍 Мониторинг логов

### Просмотр логов в реальном времени

```bash
# Основные логи
tail -f logs/django.log

# Логи предупреждений
tail -f logs/alerts.log

# Логи импорта Mango
tail -f logs/mango_import.log
```

### Поиск по логам

```bash
# Поиск ошибок
grep "ERROR" logs/django.log

# Поиск логинов
grep "\[LOGIN\]" logs/django.log

# Поиск по пользователю
grep "\[USER\]" logs/django.log
```

## 🛠️ Настройка для разработки

### Windows PowerShell

```powershell
# Установка кодировки UTF-8
chcp 65001

# Запуск сервера разработки
python manage.py runserver
```

### Windows Command Prompt

```cmd
# Установка кодировки UTF-8
chcp 65001

# Запуск сервера разработки
python manage.py runserver
```

## 🔧 Переменные окружения

Добавьте в `.env` файл:

```env
# Кодировка для Python
PYTHONIOENCODING=utf-8

# Настройки логирования
LOG_LEVEL=INFO
LOG_ENCODING=utf-8
```

## 📊 Мониторинг производительности

Система логирования включает мониторинг:

- ⏱️ Время выполнения запросов
- 🔢 Количество запросов к БД
- 💾 Использование памяти
- 🖥️ Загрузка CPU
- 💿 Использование диска

## 🚀 Продакшен настройки

Для продакшена рекомендуется:

1. **Ротация логов**
   ```python
   'handlers': {
       'file': {
           'class': 'logging.handlers.RotatingFileHandler',
           'maxBytes': 10*1024*1024,  # 10MB
           'backupCount': 5,
           'encoding': 'utf-8',
       }
   }
   ```

2. **Централизованное логирование**
   - Отправка логов в ELK Stack
   - Интеграция с Grafana
   - Алерты через Telegram

3. **Безопасность логов**
   - Маскирование чувствительных данных
   - Шифрование лог-файлов
   - Ограничение доступа к логам

## ✅ Проверка работоспособности

После настройки проверьте:

1. ✅ Логи создаются без ошибок кодировки
2. ✅ Эмодзи корректно заменяются
3. ✅ Telegram уведомления отправляются
4. ✅ Консольный вывод читаем
5. ✅ Лог-файлы открываются в текстовых редакторах

## 🆘 Устранение неполадок

### Проблема: Логи не создаются
```bash
# Проверьте права доступа
ls -la logs/

# Создайте папку логов
mkdir -p logs
chmod 755 logs
```

### Проблема: Кодировка в логах
```bash
# Проверьте кодировку файла
file logs/django.log

# Перекодируйте файл
iconv -f cp1251 -t utf-8 logs/django.log > logs/django_utf8.log
```

### Проблема: Telegram не отправляется
```bash
# Проверьте переменные окружения
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Проверьте подключение к интернету
ping api.telegram.org
```

## 📚 Дополнительные ресурсы

- [Django Logging Documentation](https://docs.djangoproject.com/en/5.2/topics/logging/)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Windows UTF-8 Support](https://docs.microsoft.com/en-us/windows/uwp/design/globalizing/use-utf8-code-page)

---

*Документация обновлена: 6 июля 2025 г.* 