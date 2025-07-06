# 📚 API Документация CRM системы

## 🔗 Общая информация

**Base URL**: `https://localhost:8000` (через API Gateway)

**Аутентификация**: JWT токены через HTTP-only cookies

**Формат данных**: JSON

**Кодировка**: UTF-8

---

## 🔐 Аутентификация

### Вход в систему

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**Ответ:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "city": "Москва"
  }
}
```

### Выход из системы

```http
POST /api/v1/auth/logout/
```

**Ответ:**
```json
{
  "success": true,
  "message": "Успешный выход из системы"
}
```

---

## 👥 User Service API

### Получение списка пользователей

```http
GET /api/v1/users/
Authorization: Bearer <token>
```

**Параметры запроса:**
- `page` - номер страницы (по умолчанию: 1)
- `page_size` - размер страницы (по умолчанию: 20)
- `search` - поиск по имени пользователя
- `role` - фильтр по роли
- `city` - фильтр по городу

**Ответ:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Администратор",
      "last_name": "Системы",
      "role": {
        "id": 1,
        "name": "admin",
        "display_name": "Администратор"
      },
      "city": {
        "id": 1,
        "name": "Москва"
      },
      "is_active": true,
      "date_joined": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Создание пользователя

```http
POST /api/v1/users/
Content-Type: application/json
Authorization: Bearer <token>

{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password123",
  "first_name": "Иван",
  "last_name": "Иванов",
  "role": 2,
  "city": 1
}
```

**Ответ:**
```json
{
  "id": 156,
  "username": "new_user",
  "email": "user@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "role": {
    "id": 2,
    "name": "master",
    "display_name": "Мастер"
  },
  "city": {
    "id": 1,
    "name": "Москва"
  },
  "is_active": true,
  "date_joined": "2024-01-20T14:25:00Z"
}
```

### Обновление пользователя

```http
PUT /api/v1/users/1/
Content-Type: application/json
Authorization: Bearer <token>

{
  "first_name": "Обновленное имя",
  "last_name": "Обновленная фамилия",
  "email": "updated@example.com"
}
```

### Удаление пользователя

```http
DELETE /api/v1/users/1/
Authorization: Bearer <token>
```

---

## 🎯 Zayavki Service API

### Получение списка заявок

```http
GET /api/v1/zayavki/
Authorization: Bearer <token>
```

**Параметры запроса:**
- `status` - статус заявки (new, in_progress, completed, cancelled)
- `type` - тип заявки
- `master` - ID мастера
- `city` - город
- `date_from` - дата начала (YYYY-MM-DD)
- `date_to` - дата окончания (YYYY-MM-DD)
- `search` - поиск по описанию

**Ответ:**
```json
{
  "count": 1250,
  "next": "http://localhost:8000/api/v1/zayavki/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Ремонт холодильника",
      "description": "Не работает компрессор",
      "status": "in_progress",
      "priority": "high",
      "type": {
        "id": 1,
        "name": "Ремонт бытовой техники"
      },
      "master": {
        "id": 5,
        "name": "Петров И.С."
      },
      "client": {
        "name": "Иванова М.П.",
        "phone": "+7 (999) 123-45-67",
        "address": "ул. Ленина, 15, кв. 25"
      },
      "city": {
        "id": 1,
        "name": "Москва"
      },
      "created_at": "2024-01-20T09:15:00Z",
      "updated_at": "2024-01-20T14:30:00Z",
      "estimated_cost": 5000,
      "actual_cost": 4800,
      "files": [
        {
          "id": 1,
          "name": "photo1.jpg",
          "url": "/media/zayavki/photo1.jpg"
        }
      ]
    }
  ]
}
```

### Создание заявки

```http
POST /api/v1/zayavki/
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Ремонт стиральной машины",
  "description": "Не отжимает белье",
  "type": 2,
  "master": 5,
  "client": {
    "name": "Сидорова А.В.",
    "phone": "+7 (999) 987-65-43",
    "address": "ул. Пушкина, 10, кв. 12"
  },
  "priority": "medium",
  "estimated_cost": 3000
}
```

### Обновление статуса заявки

```http
PATCH /api/v1/zayavki/1/
Content-Type: application/json
Authorization: Bearer <token>

{
  "status": "completed",
  "actual_cost": 2800,
  "completion_notes": "Ремонт завершен успешно"
}
```

### Загрузка файлов к заявке

```http
POST /api/v1/zayavkafiles/
Content-Type: multipart/form-data
Authorization: Bearer <token>

{
  "zayavka": 1,
  "file": <file_upload>,
  "description": "Фото неисправности"
}
```

---

## 💰 Finance Service API

### Получение транзакций

```http
GET /api/v1/finance/tranzakcii/
Authorization: Bearer <token>
```

**Параметры запроса:**
- `type` - тип транзакции
- `master` - ID мастера
- `date_from` - дата начала
- `date_to` - дата окончания
- `amount_min` - минимальная сумма
- `amount_max` - максимальная сумма

**Ответ:**
```json
{
  "count": 450,
  "next": "http://localhost:8000/api/v1/finance/tranzakcii/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "amount": 5000,
      "type": {
        "id": 1,
        "name": "Оплата заявки",
        "category": "income"
      },
      "zayavka": {
        "id": 1,
        "title": "Ремонт холодильника"
      },
      "master": {
        "id": 5,
        "name": "Петров И.С."
      },
      "description": "Оплата за ремонт холодильника",
      "date": "2024-01-20T15:30:00Z",
      "status": "completed"
    }
  ]
}
```

### Создание транзакции

```http
POST /api/v1/finance/tranzakcii/
Content-Type: application/json
Authorization: Bearer <token>

{
  "amount": 5000,
  "type": 1,
  "zayavka": 1,
  "master": 5,
  "description": "Оплата за ремонт",
  "date": "2024-01-20T15:30:00Z"
}
```

### Получение выплат мастерам

```http
GET /api/v1/finance/payouts/
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "master": {
        "id": 5,
        "name": "Петров И.С."
      },
      "amount": 15000,
      "period_start": "2024-01-01",
      "period_end": "2024-01-31",
      "status": "pending",
      "created_at": "2024-02-01T10:00:00Z",
      "paid_at": null
    }
  ]
}
```

---

## 📊 Статистика и отчеты

### Статистика по заявкам

```http
GET /api/v1/reports/zayavki-stats/
Authorization: Bearer <token>
```

**Параметры:**
- `date_from` - дата начала периода
- `date_to` - дата окончания периода
- `city` - город (опционально)
- `master` - мастер (опционально)

**Ответ:**
```json
{
  "total_zayavki": 1250,
  "completed": 980,
  "in_progress": 200,
  "cancelled": 70,
  "total_revenue": 2500000,
  "average_cost": 2000,
  "by_status": {
    "new": 50,
    "in_progress": 200,
    "completed": 980,
    "cancelled": 70
  },
  "by_type": {
    "Ремонт бытовой техники": 600,
    "Ремонт электроники": 400,
    "Установка техники": 250
  }
}
```

### Финансовая статистика

```http
GET /api/v1/reports/finance-stats/
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "total_income": 2500000,
  "total_expenses": 1800000,
  "net_profit": 700000,
  "by_month": [
    {
      "month": "2024-01",
      "income": 2500000,
      "expenses": 1800000,
      "profit": 700000
    }
  ],
  "top_masters": [
    {
      "master": "Петров И.С.",
      "revenue": 150000,
      "completed_zayavki": 25
    }
  ]
}
```

---

## 🔍 Поиск и фильтрация

### Глобальный поиск

```http
GET /api/v1/search/
Authorization: Bearer <token>
```

**Параметры:**
- `q` - поисковый запрос
- `type` - тип объекта (zayavki, users, finance)

**Ответ:**
```json
{
  "zayavki": [
    {
      "id": 1,
      "title": "Ремонт холодильника",
      "status": "completed",
      "score": 0.95
    }
  ],
  "users": [
    {
      "id": 5,
      "name": "Петров И.С.",
      "role": "master",
      "score": 0.88
    }
  ]
}
```

---

## ⚠️ Обработка ошибок

### Стандартные HTTP коды

- `200` - Успешный запрос
- `201` - Объект создан
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Объект не найден
- `500` - Внутренняя ошибка сервера

### Пример ошибки валидации

```json
{
  "error": "validation_error",
  "message": "Ошибка валидации данных",
  "details": {
    "email": ["Это поле обязательно."],
    "phone": ["Неверный формат номера телефона."]
  }
}
```

### Пример ошибки доступа

```json
{
  "error": "permission_denied",
  "message": "У вас нет прав для выполнения этого действия",
  "required_permission": "can_edit_zayavki"
}
```

---

## 🚀 Примеры использования

### JavaScript (Fetch API)

```javascript
// Аутентификация
const login = async (username, password) => {
  const response = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
    credentials: 'include'
  });
  return response.json();
};

// Получение заявок
const getZayavki = async (params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const response = await fetch(`/api/v1/zayavki/?${queryString}`, {
    credentials: 'include'
  });
  return response.json();
};

// Создание заявки
const createZayavka = async (zayavkaData) => {
  const response = await fetch('/api/v1/zayavki/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(zayavkaData),
    credentials: 'include'
  });
  return response.json();
};
```

### Python (requests)

```python
import requests

# Базовый URL
BASE_URL = 'https://localhost:8000'

# Сессия с cookies
session = requests.Session()

# Аутентификация
def login(username, password):
    response = session.post(f'{BASE_URL}/api/v1/auth/login/', json={
        'username': username,
        'password': password
    })
    return response.json()

# Получение заявок
def get_zayavki(params=None):
    response = session.get(f'{BASE_URL}/api/v1/zayavki/', params=params)
    return response.json()

# Создание заявки
def create_zayavka(data):
    response = session.post(f'{BASE_URL}/api/v1/zayavki/', json=data)
    return response.json()
```

### cURL

```bash
# Аутентификация
curl -X POST https://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}' \
  -c cookies.txt

# Получение заявок
curl -X GET https://localhost:8000/api/v1/zayavki/ \
  -b cookies.txt

# Создание заявки
curl -X POST https://localhost:8000/api/v1/zayavki/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Ремонт стиральной машины",
    "description": "Не отжимает белье",
    "type": 2,
    "master": 5
  }'
```

---

## 📝 Примечания

1. **Аутентификация**: Все запросы (кроме login/logout) требуют аутентификации
2. **Пагинация**: Списки поддерживают пагинацию с параметрами `page` и `page_size`
3. **Фильтрация**: Большинство списков поддерживают фильтрацию по различным параметрам
4. **Поиск**: Глобальный поиск доступен через `/api/v1/search/`
5. **Файлы**: Загрузка файлов выполняется через `multipart/form-data`
6. **Валидация**: Все данные валидируются на сервере
7. **Безопасность**: Используются HTTP-only cookies для JWT токенов

---

## 🔗 Полезные ссылки

- [Swagger UI](https://localhost:8000/swagger/) - Интерактивная документация
- [Health Check](https://localhost:8000/health/) - Проверка состояния сервисов
- [Admin Panel](https://localhost:8001/admin/) - Административная панель 