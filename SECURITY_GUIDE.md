# 🔐 Руководство по безопасности CRM системы

## 🚨 Критические исправления безопасности

### ✅ Выполненные исправления

1. **Исправлен SECRET_KEY в микросервисах**
   - Удален хардкод `django-insecure-your-secret-key-here-change-in-production`
   - Добавлена проверка переменной окружения `SECRET_KEY`
   - Создан скрипт для генерации безопасных ключей

2. **Добавлена PostgreSQL вместо SQLite**
   - Настроена production база данных
   - Добавлен Redis для кэширования
   - Настроены health checks

3. **Создан CI/CD pipeline безопасности**
   - Автоматическая проверка на хардкод секретов
   - Сканирование уязвимостей с Bandit
   - Проверка зависимостей с Safety

4. **Улучшен .gitignore**
   - Защита от коммита секретов
   - Исключение временных файлов
   - Защита SSL сертификатов

## 🔧 Настройка безопасности

### 1. Генерация SECRET_KEY

```bash
# Генерация нового SECRET_KEY
python scripts/generate_secret_key.py
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `env.production`:

```bash
# Скопируйте шаблон
cp env.production .env

# Отредактируйте .env файл
nano .env
```

**Обязательные переменные:**
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
DB_PASSWORD=your-strong-database-password
MANGO_API_KEY=your-mango-api-key
MANGO_API_SALT=your-mango-api-salt
```

### 3. Запуск с безопасными настройками

```bash
# Загрузка переменных окружения
source .env

# Запуск с Docker Compose
docker-compose up -d

# Или локальный запуск
python manage.py runserver
```

## 🛡️ Дополнительные меры безопасности

### 1. SSL/TLS сертификаты

```bash
# Генерация SSL сертификатов
python scripts/generate_ssl_cert.py

# Запуск с SSL
python manage.py runserver_plus --cert-file ssl_certs/localhost.crt --key-file ssl_certs/localhost.key
```

### 2. Настройка файрвола

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. Мониторинг безопасности

```bash
# Проверка логов безопасности
tail -f logs/alerts.log

# Проверка подозрительной активности
grep "suspicious" logs/django.log
```

## 📋 Чек-лист безопасности

### ✅ Обязательные проверки перед деплоем:

- [ ] SECRET_KEY изменен и не в git
- [ ] DEBUG=False в продакшене
- [ ] ALLOWED_HOSTS настроен правильно
- [ ] SSL сертификаты установлены
- [ ] База данных защищена паролем
- [ ] API ключи не в коде
- [ ] Логирование настроено
- [ ] Мониторинг активен

### 🔍 Регулярные проверки:

- [ ] Обновление зависимостей
- [ ] Проверка логов безопасности
- [ ] Сканирование уязвимостей
- [ ] Аудит доступа
- [ ] Резервное копирование

## 🚨 Алерты безопасности

### Telegram уведомления

Система отправляет алерты в Telegram при:

- Попытках взлома
- Подозрительной активности
- Ошибках безопасности
- Критических сбоях

### Настройка алертов:

```env
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

## 🔧 Устранение проблем

### Проблема: "SECRET_KEY environment variable is required"

**Решение:**
```bash
# Сгенерируйте новый ключ
python scripts/generate_secret_key.py

# Добавьте в переменные окружения
export SECRET_KEY="your-generated-key"
```

### Проблема: "Database connection failed"

**Решение:**
```bash
# Проверьте настройки базы данных
echo $DB_HOST $DB_NAME $DB_USER

# Перезапустите PostgreSQL
docker-compose restart postgres
```

### Проблема: "SSL certificate not found"

**Решение:**
```bash
# Сгенерируйте сертификаты
python scripts/generate_ssl_cert.py

# Проверьте права доступа
chmod 600 ssl_certs/*.key
```

## 📚 Дополнительные ресурсы

- [Django Security](https://docs.djangoproject.com/en/5.2/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

## 🔄 Обновления безопасности

### Автоматические обновления:

```bash
# Обновление зависимостей
pip install --upgrade -r requirements.txt

# Проверка уязвимостей
safety check

# Сканирование кода
bandit -r .
```

### Ручные обновления:

1. Регулярно обновляйте Django и зависимости
2. Проверяйте CVE базы данных
3. Обновляйте SSL сертификаты
4. Ротация паролей и ключей

---

## ✅ Заключение

После выполнения всех рекомендаций ваша CRM система будет защищена от основных угроз безопасности. Регулярно проверяйте и обновляйте меры безопасности. 