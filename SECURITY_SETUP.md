# 🔐 Настройка безопасности CRM системы

## Обзор

Этот документ описывает настройку безопасности для CRM системы, включая SSL/TLS сертификаты, заголовки безопасности и аутентификацию.

## ✅ Выполненные улучшения

### 1. Заголовки безопасности

#### Добавленные заголовки:
- `X-Frame-Options: DENY` - защита от clickjacking
- `X-Content-Type-Options: nosniff` - защита от MIME sniffing
- `X-XSS-Protection: 1; mode=block` - защита от XSS
- `Referrer-Policy: strict-origin-when-cross-origin` - контроль referrer
- `Cross-Origin-Opener-Policy: same-origin` - изоляция окон
- `Cross-Origin-Embedder-Policy: require-corp` - изоляция ресурсов
- `Content-Security-Policy` - политика безопасности контента

#### Реализация:
- Middleware `SecurityHeadersMiddleware` в `core/middleware.py`
- Обновленные настройки в `panel/settings.py`
- Настройки Nginx в `nginx.conf`

### 2. SSL/TLS сертификаты

#### Автоматическая генерация:
- Скрипт `scripts/generate_ssl_cert.py` для создания самоподписанных сертификатов
- Поддержка Windows и Linux
- Автоматическая установка в систему Windows

#### Использование:
- Django с SSL: `python manage.py runserver_plus --cert-file ssl_certs/localhost.crt --key-file ssl_certs/localhost.key`
- Nginx с SSL: настроен в `nginx.conf`
- Docker Compose: обновлен для поддержки SSL

### 3. Аутентификация

#### JWT аутентификация:
- HTTP-only cookies для безопасности
- SameSite=Strict для защиты от CSRF
- Secure flag в продакшене
- Автоматическое обновление токенов

#### Роли и permissions:
- Детальная система ролей
- Фильтрация данных по городам
- Кастомные permission классы

## 🚀 Быстрый старт

### 1. Генерация SSL сертификатов

```bash
# Автоматическая генерация
python scripts/generate_ssl_cert.py

# Или вручную
openssl genrsa -out ssl_certs/localhost.key 2048
openssl req -new -x509 -key ssl_certs/localhost.key -out ssl_certs/localhost.crt -days 365
```

### 2. Запуск с SSL

#### Windows:
```bash
start_ssl_server.bat
```

#### Linux/Mac:
```bash
python scripts/start_ssl_server.py
```

#### Docker:
```bash
docker-compose up -d
```

### 3. Проверка безопасности

```bash
# Проверка заголовков
curl -I https://localhost:8000/api/health/

# Проверка SSL
openssl s_client -connect localhost:8000 -servername localhost
```

## 🔧 Конфигурация

### Django Settings

```python
# Security settings - ВСЕГДА активны
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Дополнительные заголовки
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp'

# Настройки сессий
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

### Nginx Configuration

```nginx
# SSL настройки
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Rate limiting
limit_req zone=api burst=10 nodelay;
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

## 🛡️ Мониторинг безопасности

### Логирование

```python
# Мониторинг подозрительной активности
class SecurityMonitoringMiddleware:
    def _check_suspicious_activity(self, request):
        # Rate limiting
        # Подозрительные заголовки
        # Аномальная активность
```

### Алерты

```python
# Telegram алерты для безопасности
send_business_alert(
    event_type='security',
    description='Подозрительная активность',
    user_info='IP: 192.168.1.1',
    additional_data={'path': '/api/login/', 'attempts': 10}
)
```

## 📋 Чек-лист безопасности

### ✅ Обязательные проверки:

- [ ] SSL сертификаты настроены
- [ ] Заголовки безопасности добавлены
- [ ] JWT аутентификация работает
- [ ] Rate limiting настроен
- [ ] CORS настроен правильно
- [ ] CSRF защита активна
- [ ] Логирование безопасности включено
- [ ] Алерты настроены

### 🔍 Тестирование:

```bash
# Проверка заголовков
curl -I https://localhost:8000/api/health/

# Проверка SSL
openssl s_client -connect localhost:8000

# Проверка аутентификации
curl -X POST https://localhost:8000/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{"login":"test","password":"test"}'

# Проверка защищенных endpoints
curl -H "Cookie: jwt=token" https://localhost:8000/api/v1/me/
```

## 🚨 Устранение проблем

### Проблема: "Missing security headers"

**Решение:**
1. Убедитесь, что `SecurityHeadersMiddleware` добавлен в `MIDDLEWARE`
2. Проверьте, что middleware выполняется после `SecurityMiddleware`

### Проблема: "SSL certificate not found"

**Решение:**
1. Запустите `python scripts/generate_ssl_cert.py`
2. Убедитесь, что OpenSSL установлен
3. Проверьте права доступа к файлам сертификатов

### Проблема: "Unauthorized: /api/v1/me/"

**Решение:**
1. Проверьте JWT токен в cookies
2. Убедитесь, что пользователь активен
3. Проверьте настройки аутентификации

## 📚 Дополнительные ресурсы

- [Django Security](https://docs.djangoproject.com/en/5.2/topics/security/)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [SSL/TLS Best Practices](https://ssl-config.mozilla.org/)
- [JWT Security](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

## 🔄 Обновления безопасности

### Регулярные проверки:
- Обновление зависимостей
- Проверка уязвимостей
- Обновление SSL сертификатов
- Аудит логов безопасности

### Автоматизация:
- CI/CD pipeline с проверками безопасности
- Автоматическое сканирование уязвимостей
- Мониторинг аномальной активности 