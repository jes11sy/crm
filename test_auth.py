#!/usr/bin/env python3
"""
Тестовый скрипт для проверки аутентификации через API Gateway
"""

import requests
import json

# URL API Gateway
GATEWAY_URL = "http://localhost:8000"

def test_auth():
    """Тестирование аутентификации"""
    print("=== Тестирование аутентификации ===")
    
    # 1. Попытка входа
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус входа: {response.status_code}")
        print(f"Ответ: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            
            if access_token:
                print(f"Получен токен: {access_token[:50]}...")
                
                # 2. Тестирование защищенного endpoint
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Тест /api/v1/users/
                print("\n=== Тестирование /api/v1/users/ ===")
                users_response = requests.get(
                    f"{GATEWAY_URL}/api/v1/users/",
                    headers=headers
                )
                
                print(f"Статус /api/v1/users/: {users_response.status_code}")
                print(f"Ответ: {users_response.text}")
                
                # Тест /api/v1/gorod/
                print("\n=== Тестирование /api/v1/gorod/ ===")
                gorod_response = requests.get(
                    f"{GATEWAY_URL}/api/v1/gorod/",
                    headers=headers
                )
                
                print(f"Статус /api/v1/gorod/: {gorod_response.status_code}")
                print(f"Ответ: {gorod_response.text}")
                
            else:
                print("Токен не найден в ответе")
        else:
            print("Ошибка входа")
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")

def test_health():
    """Тестирование health check"""
    print("\n=== Тестирование health check ===")
    
    try:
        response = requests.get(f"{GATEWAY_URL}/health/")
        print(f"Статус health: {response.status_code}")
        print(f"Ответ: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")

if __name__ == "__main__":
    test_health()
    test_auth() 