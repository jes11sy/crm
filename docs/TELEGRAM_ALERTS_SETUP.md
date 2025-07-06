# Настройка Telegram-алертов для CRM-системы

## Обзор

Система Telegram-алертов позволяет получать уведомления о важных событиях в CRM-системе в реальном времени через Telegram-бота.

## Типы алертов

### 1. Ошибки (Error Alerts)
- **Когда отправляются**: При возникновении ошибок 500, исключений, критических сбоев
- **Содержание**: Детальная информация об ошибке, путь запроса, пользователь, дополнительная информация
- **Пример**: Ошибка в API, проблемы с базой данных, необработанные исключения

### 2. Бизнес-события (Business Alerts)
- **Когда отправляются**: При важных бизнес-операциях
- **Содержание**: Информация о событии, пользователь, детали операции
- **Примеры**: Вход пользователей, создание заявок, финансовые операции

### 3. Простые сообщения (Info Alerts)
- **Когда отправляются**: Для тестирования и информационных уведомлений
- **Содержание**: Простые текстовые сообщения

## Настройка

### 1. Создание Telegram-бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 2. Получение Chat ID

#### Способ 1: Через @userinfobot
1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Бот вернет ваш Chat ID

#### Способ 2: Через API
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

### 3. Настройка переменных окружения

Добавьте в `.env` файл или настройте переменные окружения:

```bash
# Telegram Bot Settings
TELEGRAM_BOT_TOKEN=8196080486:AAHhtoncj5Ne_Cdou77rpV4xnHrVBNZgBr0
TELEGRAM_CHAT_ID=1802367546
TELEGRAM_ALERTS_ENABLED=True
TELEGRAM_ERROR_ALERTS=True
TELEGRAM_BUSINESS_ALERTS=True
```

### 4. Настройки в Django

Настройки уже добавлены в `panel/settings.py`:

```python
# Telegram Alert Settings
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8196080486:AAHhtoncj5Ne_Cdou77rpV4xnHrVBNZgBr0')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '1802367546')
TELEGRAM_ALERTS_ENABLED = os.environ.get('TELEGRAM_ALERTS_ENABLED', 'True').lower() == 'true'
TELEGRAM_ERROR_ALERTS = os.environ.get('TELEGRAM_ERROR_ALERTS', 'True').lower() == 'true'
TELEGRAM_BUSINESS_ALERTS = os.environ.get('TELEGRAM_BUSINESS_ALERTS', 'True').lower() == 'true'
```

## Использование

### 1. Автоматические алерты

Система автоматически отправляет алерты при:
- Ошибках 500 и исключениях (через middleware)
- Входе пользователей в систему
- Критических сбоях в работе приложения

### 2. Ручная отправка алертов

#### Через Python код:
```python
from core.utils import send_telegram_alert, send_error_alert, send_business_alert

# Простое сообщение
send_telegram_alert("Важное уведомление!")

# Алерт об ошибке
send_error_alert(
    error=exception,
    request_path="/api/endpoint",
    user_info="user@example.com",
    additional_info={"detail": "Дополнительная информация"}
)

# Бизнес-событие
send_business_alert(
    event_type="new_zayavka",
    description="Создана новая заявка",
    user_info="admin",
    additional_data={"zayavka_id": 12345}
)
```

#### Через API:
```bash
# Тестирование алертов
curl -X POST http://localhost:8000/api/v1/test-telegram-alert/ \
  -H "Content-Type: application/json" \
  -d '{"type": "info", "message": "Тестовое сообщение"}'

# Искусственное создание ошибки
curl -X POST http://localhost:8000/api/v1/trigger-test-error/
```

### 3. Тестирование

Запустите скрипт тестирования:

```bash
python scripts/test_telegram_alerts.py
```

## API Endpoints

### POST /api/v1/test-telegram-alert/
Тестирует отправку алертов в Telegram.

**Параметры:**
- `type` (string): Тип алерта (`info`, `error`, `business`)
- `message` (string): Текст сообщения
- `timestamp` (string, optional): Временная метка

**Пример:**
```json
{
  "type": "business",
  "message": "Тестовое бизнес-событие",
  "timestamp": "2025-07-06 10:45:00"
}
```

### POST /api/v1/trigger-test-error/
Искусственно вызывает ошибку для тестирования алертов.

## Форматирование сообщений

### Ошибки
```
🚨 ОШИБКА В CRM

⏰ Время: 2025-07-06 10:45:00
❌ Ошибка: Exception: Описание ошибки
🔗 Путь: /api/endpoint
👤 Пользователь: admin

📋 Дополнительно:
• method: POST
• ip_address: 127.0.0.1
• user_agent: Mozilla/5.0...
```

### Бизнес-события
```
🔐 LOGIN

⏰ Время: 2025-07-06 10:45:00
📄 Описание: Пользователь Иван вошел в систему
👤 Пользователь: ivan (admin)

📋 Детали:
• gorod: Москва
• ip_address: 127.0.0.1
• user_agent: Mozilla/5.0...
```

## Настройка логирования

Telegram-хендлер настроен в `settings.py`:

```python
LOGGING = {
    'handlers': {
        'telegram': {
            'level': 'ERROR',
            'class': 'core.telegram_handler.TelegramLogHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['telegram'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['telegram'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
```

## Управление алертами

### Включение/отключение
- `TELEGRAM_ALERTS_ENABLED`: Общее включение/отключение алертов
- `TELEGRAM_ERROR_ALERTS`: Включение/отключение алертов об ошибках
- `TELEGRAM_BUSINESS_ALERTS`: Включение/отключение бизнес-алертов

### Фильтрация
Можно настроить фильтрацию по:
- Уровню ошибок (ERROR, WARNING, INFO)
- Типу событий
- Пользователям
- IP-адресам

## Безопасность

### Рекомендации:
1. **Не публикуйте токен бота** в публичных репозиториях
2. **Используйте переменные окружения** для хранения токена
3. **Ограничьте доступ** к боту только нужным пользователям
4. **Мониторьте логи** отправки алертов
5. **Настройте rate limiting** для предотвращения спама

### Ограничения Telegram API:
- Максимум 30 сообщений в секунду
- Максимум 4096 символов в сообщении
- Таймаут запросов: 10 секунд

## Устранение неполадок

### Проблема: Алерты не отправляются
1. Проверьте настройки `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`
2. Убедитесь, что бот добавлен в чат
3. Проверьте логи Django на ошибки отправки
4. Запустите тестовый скрипт

### Проблема: Бот не отвечает
1. Проверьте правильность токена
2. Убедитесь, что бот не заблокирован
3. Проверьте права бота в чате

### Проблема: Слишком много алертов
1. Настройте фильтрацию по уровню важности
2. Увеличьте пороги для срабатывания
3. Настройте группировку похожих алертов

## Расширение функциональности

### Добавление новых типов алертов:
1. Создайте новую функцию в `core/utils.py`
2. Добавьте эмодзи в `emoji_map`
3. Настройте условия отправки
4. Обновите документацию

### Интеграция с другими сервисами:
- Slack (аналогично Telegram)
- Email-уведомления
- SMS-уведомления
- Webhook-уведомления

## Мониторинг и аналитика

### Метрики для отслеживания:
- Количество отправленных алертов
- Успешность доставки
- Время отклика
- Типы ошибок

### Логирование:
Все попытки отправки алертов логируются в:
- `logs/django.log` - общие логи
- `logs/alerts.log` - логи алертов
- Консоль Django (в DEBUG режиме) 