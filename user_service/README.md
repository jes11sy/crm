# User Service - Микросервис пользователей

Микросервис для управления пользователями, ролями, мастерами и городами в CRM системе.

## 🚀 Быстрый старт

### Требования
- Python 3.8+
- Django 5.2+
- PostgreSQL (рекомендуется) или SQLite (для разработки)

### Установка и запуск

1. **Клонирование и установка зависимостей:**
```bash
cd user_service
pip install -r requirements.txt
```

2. **Настройка переменных окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл под ваши настройки
```

3. **Применение миграций:**
```bash
python manage.py migrate
```

4. **Создание суперпользователя (опционально):**
```bash
python manage.py createsuperuser
```

5. **Запуск сервера:**
```bash
python manage.py runserver 8001
```

Сервер будет доступен по адресу: http://localhost:8001

## 📚 API Документация

### Swagger UI
- **URL:** http://localhost:8001/swagger/
- Интерактивная документация API

### ReDoc
- **URL:** http://localhost:8001/redoc/
- Альтернативная документация API

## 🔧 API Endpoints

### Города (Gorod)
```
GET    /api/v1/gorods/           # Список городов
POST   /api/v1/gorods/           # Создание города
GET    /api/v1/gorods/{id}/      # Детали города
PUT    /api/v1/gorods/{id}/      # Обновление города
DELETE /api/v1/gorods/{id}/      # Удаление города
```

### Роли (Roli)
```
GET    /api/v1/rolis/            # Список ролей
POST   /api/v1/rolis/            # Создание роли
GET    /api/v1/rolis/{id}/       # Детали роли
PUT    /api/v1/rolis/{id}/       # Обновление роли
DELETE /api/v1/rolis/{id}/       # Удаление роли
```

### Пользователи (Polzovateli)
```
GET    /api/v1/polzovatelis/     # Список пользователей
POST   /api/v1/polzovatelis/     # Создание пользователя
GET    /api/v1/polzovatelis/{id}/ # Детали пользователя
PUT    /api/v1/polzovatelis/{id}/ # Обновление пользователя
DELETE /api/v1/polzovatelis/{id}/ # Удаление пользователя
POST   /api/v1/polzovatelis/authenticate/ # Аутентификация
```

### Мастера (Master)
```
GET    /api/v1/masters/          # Список мастеров
POST   /api/v1/masters/          # Создание мастера
GET    /api/v1/masters/{id}/     # Детали мастера
PUT    /api/v1/masters/{id}/     # Обновление мастера
DELETE /api/v1/masters/{id}/     # Удаление мастера
POST   /api/v1/masters/authenticate/ # Аутентификация мастера
```

## 💡 Примеры использования

### Создание города
```bash
curl -X POST "http://localhost:8001/api/v1/gorods/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Москва"}'
```

### Создание роли
```bash
curl -X POST "http://localhost:8001/api/v1/rolis/" \
     -H "Content-Type: application/json" \
     -d '{"name": "admin"}'
```

### Создание пользователя
```bash
curl -X POST "http://localhost:8001/api/v1/polzovatelis/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Иван Иванов",
       "login": "ivan",
       "password": "password123",
       "gorod_id": 1,
       "rol_id": 1,
       "is_active": true
     }'
```

### Аутентификация пользователя
```bash
curl -X POST "http://localhost:8001/api/v1/polzovatelis/authenticate/" \
     -H "Content-Type: application/json" \
     -d '{
       "login": "ivan",
       "password": "password123"
     }'
```

### Создание мастера
```bash
curl -X POST "http://localhost:8001/api/v1/masters/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Петр Петров",
       "phone": "+79001234567",
       "login": "petr_master",
       "password": "masterpass123",
       "gorod_id": 1,
       "is_active": true
     }'
```

## 🧪 Тестирование

### Запуск тестов
```bash
python manage.py test
```

### Запуск тестов с покрытием
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🐳 Docker

### Сборка образа
```bash
docker build -t user-service .
```

### Запуск контейнера
```bash
docker run -p 8001:8001 user-service
```

### Docker Compose
```bash
docker-compose up -d
```

## 🔒 Безопасность

### Аутентификация
- Все API endpoints требуют аутентификации (кроме Swagger/ReDoc)
- Поддерживается Session Authentication и Basic Authentication
- Пароли автоматически хешируются при создании/обновлении

### CORS
- Настроен для работы с фронтендом на localhost:3000
- В продакшене настройте CORS_ALLOWED_ORIGINS под ваши домены

## 📊 Мониторинг

### Логирование
- Логи сохраняются в `logs/user_service.log`
- Уровень логирования: INFO для Django, DEBUG для приложения users

### Health Check
```bash
curl http://localhost:8001/admin/
```

## 🔄 Интеграция с другими сервисами

### Пример интеграции из Python
```python
import requests

# Создание пользователя
def create_user(name, login, password, gorod_id, rol_id):
    url = "http://localhost:8001/api/v1/polzovatelis/"
    data = {
        "name": name,
        "login": login,
        "password": password,
        "gorod_id": gorod_id,
        "rol_id": rol_id,
        "is_active": True
    }
    response = requests.post(url, json=data)
    return response.json()

# Аутентификация пользователя
def authenticate_user(login, password):
    url = "http://localhost:8001/api/v1/polzovatelis/authenticate/"
    data = {
        "login": login,
        "password": password
    }
    response = requests.post(url, json=data)
    return response.json()
```

### Пример интеграции из JavaScript
```javascript
// Создание пользователя
async function createUser(userData) {
    const response = await fetch('http://localhost:8001/api/v1/polzovatelis/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });
    return response.json();
}

// Аутентификация пользователя
async function authenticateUser(login, password) {
    const response = await fetch('http://localhost:8001/api/v1/polzovatelis/authenticate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ login, password })
    });
    return response.json();
}
```

## 🏗️ Архитектура

### Модели данных
- **Gorod** - Города
- **Roli** - Роли пользователей
- **Polzovateli** - Пользователи системы
- **Master** - Мастера (с автоматической синхронизацией с Polzovateli)

### Особенности
- Автоматическое хеширование паролей
- Синхронизация мастеров с пользователями
- Валидация телефонных номеров
- Индексы для оптимизации запросов

## 🚀 Развертывание

### Переменные окружения
```bash
# Основные настройки
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# База данных
DB_NAME=user_service_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### Продакшен
1. Настройте PostgreSQL
2. Установите переменные окружения
3. Запустите с Gunicorn или uWSGI
4. Настройте Nginx как reverse proxy

## 📝 Лицензия

MIT License

## 🤝 Поддержка

Для вопросов и предложений создавайте issues в репозитории проекта. 