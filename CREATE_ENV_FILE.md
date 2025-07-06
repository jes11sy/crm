# 🔧 Создание файла .env на сервере

## Проблема:
Docker Compose не может прочитать файл `.env` из-за неправильной кодировки.

## Решение:

### 1. Удалите старый файл .env:
```bash
rm .env
```

### 2. Создайте новый файл .env:
```bash
cat > .env << 'EOF'
# Основные настройки Django
SECRET_KEY=PShk+/b+8D2W*-u!TE568w0bxtMS-2@2k3i.2IK9I>YMiN>eaZ
DEBUG=False
ALLOWED_HOSTS=crm.lead-schem.ru,www.crm.lead-schem.ru,localhost,127.0.0.1

# Настройки базы данных
DB_NAME=crm_production
DB_USER=crm_user
DB_PASSWORD=1740
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://crm.lead-schem.ru,https://www.crm.lead-schem.ru
CSRF_TRUSTED_ORIGINS=https://crm.lead-schem.ru,https://www.crm.lead-schem.ru

# JWT
JWT_SECRET_KEY=PShk+/b+8D2W*-u!TE568w0bxtMS-2@2k3i.2IK9I>YMiN>eaZ
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email
CERTBOT_EMAIL=defouz03@gmail.com

# Временная зона
TIME_ZONE=Europe/Moscow
LANGUAGE_CODE=ru-ru

# Безопасность
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
EOF
```

### 3. Проверьте кодировку:
```bash
file .env
```
Должно показать: `ASCII text`

### 4. Перезапустите сервисы:
```bash
docker-compose down
docker-compose up -d
```

### 5. Проверьте статус:
```bash
docker-compose ps
docker-compose logs -f
```

## ✅ Результат:
- Все сервисы должны запуститься без ошибок
- Нет проблем с кодировкой файла .env
- CRM доступен по адресу: http://crm.lead-schem.ru 