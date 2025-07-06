# 🚀 Руководство по обновлению CRM на сервере

## 📋 Что обновлено в репозитории

### ✅ Структура проекта
- Микросервисная архитектура с API Gateway
- Отдельные сервисы: User Service, Zayavki Service, Finance Service
- Frontend на React + TypeScript + Ant Design
- Docker Compose для развертывания
- CI/CD pipeline с GitHub Actions

### ✅ Зависимости
- **Backend**: Django 5.2.1, DRF 3.15+, PostgreSQL, Redis
- **Frontend**: React 18.2, TypeScript, Ant Design 5.26.3
- **DevOps**: Docker, Nginx, SSL сертификаты

### ✅ Безопасность
- JWT аутентификация с HTTP-only cookies
- CORS настройки
- SSL/TLS поддержка
- Система ролей и permissions

---

## 🔄 Обновление на сервере Ubuntu

### 1. Подготовка (если проект еще не клонирован)

```bash
# Клонирование репозитория
git clone https://github.com/jes11sy/crm.git
cd crm

# Установка Docker и Docker Compose (если не установлены)
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Настройка переменных окружения

```bash
# Создание .env файла
cp env.example .env

# Редактирование .env файла
nano .env
```

**Содержимое .env файла:**
```bash
# Основные настройки
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=crm.lead-schem.ru,www.crm.lead-schem.ru

# База данных
DB_NAME=crm_production
DB_USER=crm_user
DB_PASSWORD=your-secure-password

# CORS
CORS_ALLOWED_ORIGINS=https://crm.lead-schem.ru,https://www.crm.lead-schem.ru

# Email для SSL сертификатов
CERTBOT_EMAIL=your-email@example.com
```

### 3. Обновление существующего проекта

```bash
# Остановка сервисов
docker-compose down

# Обновление кода с GitHub
git pull origin main

# Пересборка и запуск
docker-compose up -d --build

# Проверка логов
docker-compose logs -f
```

### 4. Применение миграций (если есть)

```bash
# User Service
docker-compose exec user-service python manage.py migrate

# Zayavki Service  
docker-compose exec zayavki-service python manage.py migrate

# Finance Service
docker-compose exec finance-service python manage.py migrate
```

### 5. Создание суперпользователя (если нужно)

```bash
docker-compose exec user-service python manage.py createsuperuser
```

---

## 🔧 Устранение проблем

### Проблема: Ошибки сборки frontend
```bash
# Очистка node_modules
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..

# Пересборка
docker-compose build frontend
docker-compose up -d frontend
```

### Проблема: Конфликты версий TypeScript
```bash
# Синхронизация package.json и package-lock.json
cd frontend
npm install
cd ..
docker-compose up -d --build
```

### Проблема: Ошибки базы данных
```bash
# Проверка подключения к БД
docker-compose exec postgres psql -U crm_user -d crm_production

# Сброс миграций (если нужно)
docker-compose exec user-service python manage.py migrate --fake-initial
```

---

## 📊 Мониторинг и проверка

### Проверка статуса сервисов
```bash
# Статус контейнеров
docker-compose ps

# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f api-gateway
```

### Проверка доступности
```bash
# API Gateway
curl http://localhost:8000/health/

# User Service
curl http://localhost:8001/swagger/

# Frontend
curl http://localhost:3000/
```

### Проверка SSL (если настроен)
```bash
# Проверка сертификата
openssl s_client -connect crm.lead-schem.ru:443 -servername crm.lead-schem.ru

# Проверка заголовков безопасности
curl -I https://crm.lead-schem.ru/api/health/
```

---

## 🚀 Автоматическое обновление

### Скрипт для автоматического обновления

Создайте файл `update.sh`:
```bash
#!/bin/bash

echo "🔄 Обновление CRM проекта..."

# Остановка сервисов
docker-compose down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose up -d --build

# Применение миграций
docker-compose exec user-service python manage.py migrate --noinput
docker-compose exec zayavki-service python manage.py migrate --noinput
docker-compose exec finance-service python manage.py migrate --noinput

# Проверка статуса
docker-compose ps

echo "✅ Обновление завершено!"
```

Сделайте скрипт исполняемым:
```bash
chmod +x update.sh
```

Запуск обновления:
```bash
./update.sh
```

---

## 📝 Полезные команды

### Управление сервисами
```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Перезапуск конкретного сервиса
docker-compose restart api-gateway

# Просмотр ресурсов
docker-compose top
```

### Работа с логами
```bash
# Логи всех сервисов
docker-compose logs -f

# Логи за последние 100 строк
docker-compose logs --tail=100

# Логи с временными метками
docker-compose logs -f -t
```

### Резервное копирование
```bash
# Бэкап базы данных
docker-compose exec postgres pg_dump -U crm_user crm_production > backup.sql

# Восстановление из бэкапа
docker-compose exec -T postgres psql -U crm_user crm_production < backup.sql
```

---

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус контейнеров: `docker-compose ps`
3. Проверьте ресурсы: `docker system df`
4. Очистите неиспользуемые ресурсы: `docker system prune -a`

---

## 📞 Контакты

- **GitHub**: https://github.com/jes11sy/crm
- **Домен**: https://crm.lead-schem.ru
- **Документация**: см. README.md и DEPLOYMENT_GUIDE.md 