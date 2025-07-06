# 🚀 CRM Микросервисная Архитектура

Полная микросервисная архитектура CRM-системы с API Gateway, построенная на Django.

> **🌐 Production**: https://crm.lead-schem.ru  
> **📦 GitHub**: https://github.com/jes11sy/crm  
> **📚 Документация**: [UPDATE_GUIDE.md](./UPDATE_GUIDE.md)

## 🔄 Обновление на сервере

### Быстрое обновление
```bash
# Автоматическое обновление
chmod +x update.sh
./update.sh
```

### Ручное обновление
```bash
# Остановка сервисов
docker-compose down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps
```

📖 **Подробное руководство**: [UPDATE_GUIDE.md](./UPDATE_GUIDE.md)

## Архитектура

### Микросервисы

1. **API Gateway** (порт 8000)
   - Единая точка входа для всех API
   - Маршрутизация запросов к микросервисам
   - Swagger документация
   - Health check

2. **User Service** (порт 8001)
   - Управление пользователями и ролями
   - Аутентификация и авторизация
   - API: `/api/v1/users/`, `/api/v1/roles/`, `/api/v1/masters/`

3. **Zayavki Service** (порт 8002)
   - Управление заявками
   - Типы заявок и файлы
   - API: `/api/v1/zayavki/`, `/api/v1/tipzayavki/`, `/api/v1/zayavkafiles/`

4. **Finance Service** (порт 8003)
   - Финансовые операции
   - Транзакции и выплаты
   - API: `/api/v1/finance/tranzakcii/`, `/api/v1/finance/payouts/`

## Запуск

### Локальная разработка

```bash
# Запуск всех сервисов через docker-compose
docker-compose up -d

# Или запуск отдельных сервисов
cd user_service && python manage.py runserver 8001
cd zayavki_service && python manage.py runserver 8002
cd financesvc && python manage.py runserver 8003
cd api_gateway && python manage.py runserver 8000
```

### Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down
```

## API Endpoints

### API Gateway (http://localhost:8000)
- `/health/` - проверка здоровья сервисов
- `/swagger/` - документация API
- `/api/v1/users/*` - прокси к User Service
- `/api/v1/zayavki/*` - прокси к Zayavki Service
- `/api/v1/finance/*` - прокси к Finance Service

### User Service (http://localhost:8001)
- `/api/v1/users/` - CRUD пользователей
- `/api/v1/roles/` - CRUD ролей
- `/api/v1/masters/` - CRUD мастеров
- `/swagger/` - документация

### Zayavki Service (http://localhost:8002)
- `/api/v1/zayavki/` - CRUD заявок
- `/api/v1/tipzayavki/` - CRUD типов заявок
- `/api/v1/zayavkafiles/` - CRUD файлов заявок
- `/swagger/` - документация

### Finance Service (http://localhost:8003)
- `/api/v1/tranzakcii/` - CRUD транзакций
- `/api/v1/tiptranzakcii/` - CRUD типов транзакций
- `/api/v1/payouts/` - CRUD выплат
- `/swagger/` - документация

## Тестирование

```bash
# Тесты User Service
cd user_service && python manage.py test usersvc.users

# Тесты Zayavki Service
cd zayavki_service && python manage.py test zayavkisvc.zayavki

# Тесты Finance Service
cd financesvc && python manage.py test financesvc.finance
```

## Структура проекта

```
дубль 2/
├── api_gateway/          # API Gateway
├── user_service/         # User Service
├── zayavki_service/      # Zayavki Service
├── financesvc/           # Finance Service
├── docker-compose.yml    # Docker Compose конфигурация
├── nginx.conf           # Nginx конфигурация
└── README.md            # Документация
```

## Разработка

### Добавление нового микросервиса

1. Создать Django проект
2. Добавить в docker-compose.yml
3. Настроить маршрутизацию в API Gateway
4. Добавить тесты

### Мониторинг

- Health check: `http://localhost:8000/health/`
- Swagger UI: `http://localhost:8000/swagger/`
- Django Admin: `http://localhost:8001/admin/`

## Технологии

- **Backend**: Django 5.2.1, Django REST Framework
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Containerization**: Docker, Docker Compose
- **Proxy**: Nginx
- **Testing**: Django Test Framework 