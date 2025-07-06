# Примеры интеграции User Service

Этот документ содержит примеры интеграции микросервиса User Service с различными технологиями и платформами.

## 🔗 REST API Интеграция

### Python (requests)

```python
import requests
import json

class UserServiceClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_city(self, name):
        """Создание города"""
        url = f"{self.base_url}/api/v1/gorods/"
        data = {"name": name}
        response = self.session.post(url, json=data)
        return response.json()
    
    def create_role(self, name):
        """Создание роли"""
        url = f"{self.base_url}/api/v1/rolis/"
        data = {"name": name}
        response = self.session.post(url, json=data)
        return response.json()
    
    def create_user(self, name, login, password, gorod_id, rol_id):
        """Создание пользователя"""
        url = f"{self.base_url}/api/v1/polzovatelis/"
        data = {
            "name": name,
            "login": login,
            "password": password,
            "gorod_id": gorod_id,
            "rol_id": rol_id,
            "is_active": True
        }
        response = self.session.post(url, json=data)
        return response.json()
    
    def authenticate_user(self, login, password):
        """Аутентификация пользователя"""
        url = f"{self.base_url}/api/v1/polzovatelis/authenticate/"
        data = {
            "login": login,
            "password": password
        }
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_users_by_city(self, gorod_id):
        """Получение пользователей по городу"""
        url = f"{self.base_url}/api/v1/polzovatelis/"
        params = {"gorod_id": gorod_id}
        response = self.session.get(url, params=params)
        return response.json()

# Пример использования
client = UserServiceClient()

# Создание данных
city = client.create_city("Москва")
role = client.create_role("admin")
user = client.create_user("Иван Иванов", "ivan", "pass123", city["id"], role["id"])

# Аутентификация
auth_result = client.authenticate_user("ivan", "pass123")
print(f"Аутентификация: {auth_result}")
```

### JavaScript/Node.js

```javascript
class UserServiceClient {
    constructor(baseUrl = 'http://localhost:8001') {
        this.baseUrl = baseUrl;
    }

    async createCity(name) {
        const response = await fetch(`${this.baseUrl}/api/v1/gorods/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name })
        });
        return response.json();
    }

    async createRole(name) {
        const response = await fetch(`${this.baseUrl}/api/v1/rolis/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name })
        });
        return response.json();
    }

    async createUser(userData) {
        const response = await fetch(`${this.baseUrl}/api/v1/polzovatelis/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        return response.json();
    }

    async authenticateUser(login, password) {
        const response = await fetch(`${this.baseUrl}/api/v1/polzovatelis/authenticate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ login, password })
        });
        return response.json();
    }

    async getUsersByCity(gorodId) {
        const response = await fetch(`${this.baseUrl}/api/v1/polzovatelis/?gorod_id=${gorodId}`);
        return response.json();
    }
}

// Пример использования
async function main() {
    const client = new UserServiceClient();

    try {
        // Создание данных
        const city = await client.createCity('Москва');
        const role = await client.createRole('admin');
        const user = await client.createUser({
            name: 'Иван Иванов',
            login: 'ivan',
            password: 'pass123',
            gorod_id: city.id,
            rol_id: role.id,
            is_active: true
        });

        // Аутентификация
        const authResult = await client.authenticateUser('ivan', 'pass123');
        console.log('Аутентификация:', authResult);

    } catch (error) {
        console.error('Ошибка:', error);
    }
}

main();
```

### PHP

```php
<?php

class UserServiceClient {
    private $baseUrl;
    
    public function __construct($baseUrl = 'http://localhost:8001') {
        $this->baseUrl = $baseUrl;
    }
    
    public function createCity($name) {
        $url = $this->baseUrl . '/api/v1/gorods/';
        $data = json_encode(['name' => $name]);
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Content-Length: ' . strlen($data)
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
    
    public function createUser($userData) {
        $url = $this->baseUrl . '/api/v1/polzovatelis/';
        $data = json_encode($userData);
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Content-Length: ' . strlen($data)
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
    
    public function authenticateUser($login, $password) {
        $url = $this->baseUrl . '/api/v1/polzovatelis/authenticate/';
        $data = json_encode([
            'login' => $login,
            'password' => $password
        ]);
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Content-Length: ' . strlen($data)
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
}

// Пример использования
$client = new UserServiceClient();

$city = $client->createCity('Москва');
$user = $client->createUser([
    'name' => 'Иван Иванов',
    'login' => 'ivan',
    'password' => 'pass123',
    'gorod_id' => $city['id'],
    'rol_id' => 1,
    'is_active' => true
]);

$authResult = $client->authenticateUser('ivan', 'pass123');
echo "Аутентификация: " . json_encode($authResult) . "\n";
?>
```

### cURL

```bash
#!/bin/bash

# Настройки
BASE_URL="http://localhost:8001"

# Функция для создания города
create_city() {
    local name=$1
    curl -X POST "${BASE_URL}/api/v1/gorods/" \
         -H "Content-Type: application/json" \
         -d "{\"name\": \"${name}\"}"
}

# Функция для создания роли
create_role() {
    local name=$1
    curl -X POST "${BASE_URL}/api/v1/rolis/" \
         -H "Content-Type: application/json" \
         -d "{\"name\": \"${name}\"}"
}

# Функция для создания пользователя
create_user() {
    local name=$1
    local login=$2
    local password=$3
    local gorod_id=$4
    local rol_id=$5
    
    curl -X POST "${BASE_URL}/api/v1/polzovatelis/" \
         -H "Content-Type: application/json" \
         -d "{
           \"name\": \"${name}\",
           \"login\": \"${login}\",
           \"password\": \"${password}\",
           \"gorod_id\": ${gorod_id},
           \"rol_id\": ${rol_id},
           \"is_active\": true
         }"
}

# Функция для аутентификации
authenticate_user() {
    local login=$1
    local password=$2
    
    curl -X POST "${BASE_URL}/api/v1/polzovatelis/authenticate/" \
         -H "Content-Type: application/json" \
         -d "{
           \"login\": \"${login}\",
           \"password\": \"${password}\"
         }"
}

# Пример использования
echo "Создание города..."
CITY_RESPONSE=$(create_city "Москва")
CITY_ID=$(echo $CITY_RESPONSE | jq -r '.id')

echo "Создание роли..."
ROLE_RESPONSE=$(create_role "admin")
ROLE_ID=$(echo $ROLE_RESPONSE | jq -r '.id')

echo "Создание пользователя..."
USER_RESPONSE=$(create_user "Иван Иванов" "ivan" "pass123" $CITY_ID $ROLE_ID)

echo "Аутентификация пользователя..."
AUTH_RESPONSE=$(authenticate_user "ivan" "pass123")
echo "Результат аутентификации: $AUTH_RESPONSE"
```

## 🔄 Интеграция с Django

### Django Settings

```python
# settings.py

# Настройки для интеграции с User Service
USER_SERVICE_CONFIG = {
    'BASE_URL': 'http://localhost:8001',
    'TIMEOUT': 30,
    'RETRY_ATTEMPTS': 3,
}

# Добавьте в MIDDLEWARE для проверки аутентификации
MIDDLEWARE = [
    # ... другие middleware
    'your_app.middleware.UserServiceAuthMiddleware',
]
```

### Django Middleware

```python
# middleware.py

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

class UserServiceAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.user_service_url = settings.USER_SERVICE_CONFIG['BASE_URL']
    
    def __call__(self, request):
        # Проверяем токен аутентификации
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_data = self.authenticate_user(token)
            if user_data:
                request.user = self.get_or_create_user(user_data)
            else:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response
    
    def authenticate_user(self, token):
        """Аутентификация пользователя через User Service"""
        try:
            url = f"{self.user_service_url}/api/v1/polzovatelis/authenticate/"
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None
    
    def get_or_create_user(self, user_data):
        """Получение или создание пользователя в локальной БД"""
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=user_data['login'],
            defaults={
                'email': user_data.get('email', ''),
                'first_name': user_data.get('name', ''),
                'is_active': user_data.get('is_active', True),
            }
        )
        return user
```

### Django Management Command

```python
# management/commands/sync_users.py

from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Синхронизация пользователей с User Service'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--gorod-id',
            type=int,
            help='ID города для синхронизации',
        )
    
    def handle(self, *args, **options):
        user_service_url = settings.USER_SERVICE_CONFIG['BASE_URL']
        
        # Получаем пользователей из User Service
        url = f"{user_service_url}/api/v1/polzovatelis/"
        params = {}
        if options['gorod_id']:
            params['gorod_id'] = options['gorod_id']
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            users_data = response.json()
            self.stdout.write(f"Получено {len(users_data['results'])} пользователей")
            
            # Здесь можно добавить логику синхронизации
            for user_data in users_data['results']:
                self.stdout.write(f"Обработка пользователя: {user_data['name']}")
                
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при получении данных: {e}')
            )
```

## 🔗 Интеграция с React

### React Hook

```javascript
// hooks/useUserService.js

import { useState, useEffect } from 'react';

const USER_SERVICE_URL = 'http://localhost:8001';

export const useUserService = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const createUser = async (userData) => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${USER_SERVICE_URL}/api/v1/polzovatelis/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const authenticateUser = async (login, password) => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${USER_SERVICE_URL}/api/v1/polzovatelis/authenticate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ login, password })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const getUsers = async (params = {}) => {
        setLoading(true);
        setError(null);
        
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = `${USER_SERVICE_URL}/api/v1/polzovatelis/${queryString ? `?${queryString}` : ''}`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return {
        createUser,
        authenticateUser,
        getUsers,
        loading,
        error
    };
};
```

### React Component

```jsx
// components/UserManagement.jsx

import React, { useState, useEffect } from 'react';
import { useUserService } from '../hooks/useUserService';

const UserManagement = () => {
    const { createUser, authenticateUser, getUsers, loading, error } = useUserService();
    const [users, setUsers] = useState([]);
    const [formData, setFormData] = useState({
        name: '',
        login: '',
        password: '',
        gorod_id: '',
        rol_id: ''
    });

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            const result = await getUsers();
            setUsers(result.results || []);
        } catch (err) {
            console.error('Ошибка загрузки пользователей:', err);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createUser(formData);
            setFormData({
                name: '',
                login: '',
                password: '',
                gorod_id: '',
                rol_id: ''
            });
            loadUsers(); // Перезагружаем список
        } catch (err) {
            console.error('Ошибка создания пользователя:', err);
        }
    };

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>Ошибка: {error}</div>;

    return (
        <div>
            <h2>Управление пользователями</h2>
            
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Имя:</label>
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        required
                    />
                </div>
                <div>
                    <label>Логин:</label>
                    <input
                        type="text"
                        name="login"
                        value={formData.login}
                        onChange={handleInputChange}
                        required
                    />
                </div>
                <div>
                    <label>Пароль:</label>
                    <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        required
                    />
                </div>
                <div>
                    <label>ID города:</label>
                    <input
                        type="number"
                        name="gorod_id"
                        value={formData.gorod_id}
                        onChange={handleInputChange}
                        required
                    />
                </div>
                <div>
                    <label>ID роли:</label>
                    <input
                        type="number"
                        name="rol_id"
                        value={formData.rol_id}
                        onChange={handleInputChange}
                        required
                    />
                </div>
                <button type="submit">Создать пользователя</button>
            </form>

            <h3>Список пользователей</h3>
            <ul>
                {users.map(user => (
                    <li key={user.id}>
                        {user.name} ({user.login}) - {user.gorod?.name}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default UserManagement;
```

## 🔗 Интеграция с другими микросервисами

### API Gateway (Kong)

```yaml
# kong.yml

_format_version: "2.1"

services:
  - name: user-service
    url: http://user-service:8001
    routes:
      - name: user-service-routes
        paths:
          - /api/v1/users
          - /api/v1/gorods
          - /api/v1/rolis
          - /api/v1/masters
    plugins:
      - name: cors
        config:
          origins: ["*"]
          methods: ["GET", "POST", "PUT", "DELETE"]
          headers: ["Content-Type", "Authorization"]
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
```

### Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  user-service:
    build: ./user-service
    ports:
      - "8001:8001"
    environment:
      - DEBUG=False
      - DB_HOST=postgres
      - DB_NAME=user_service_db
      - DB_USER=postgres
      - DB_PASSWORD=password
    depends_on:
      - postgres
    networks:
      - microservices

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=user_service_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - microservices

  api-gateway:
    image: kong:2.8
    ports:
      - "8000:8000"
      - "8443:8443"
    environment:
      - KONG_DATABASE=off
      - KONG_PROXY_ACCESS_LOG=/dev/stdout
      - KONG_ADMIN_ACCESS_LOG=/dev/stdout
      - KONG_PROXY_ERROR_LOG=/dev/stderr
      - KONG_ADMIN_ERROR_LOG=/dev/stderr
      - KONG_ADMIN_LISTEN=0.0.0.0:8001
      - KONG_ADMIN_GUI_URL=http://localhost:8002
    volumes:
      - ./kong.yml:/kong.yml
    command: kong start --conf /kong.yml
    networks:
      - microservices

volumes:
  postgres_data:

networks:
  microservices:
    driver: bridge
```

## 🔗 Мониторинг и логирование

### Prometheus Metrics

```python
# metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Метрики
REQUEST_COUNT = Counter('user_service_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('user_service_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('user_service_active_users', 'Number of active users')

class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Обновляем метрики
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
        REQUEST_DURATION.observe(duration)
        
        return response
```

### Health Check Endpoint

```python
# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

@api_view(['GET'])
def health_check(request):
    """Health check endpoint для мониторинга"""
    try:
        # Проверяем подключение к БД
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
```

Эти примеры показывают различные способы интеграции User Service с другими системами и технологиями. 