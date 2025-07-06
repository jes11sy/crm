#!/usr/bin/env python3
"""
Тестирование микросервисной архитектуры CRM
"""

import requests
import time
import json
from typing import Dict, List

class MicroservicesTester:
    def __init__(self):
        self.base_urls = {
            'api_gateway': 'http://localhost:8000',
            'user_service': 'http://localhost:8001',
            'zayavki_service': 'http://localhost:8002',
            'finance_service': 'http://localhost:8003'
        }
        
    def test_health_check(self) -> Dict[str, bool]:
        """Тестирование health check endpoints"""
        results = {}
        
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health/", timeout=5)
                results[service] = response.status_code == 200
                print(f"✅ {service}: Health check passed")
            except requests.exceptions.RequestException as e:
                results[service] = False
                print(f"❌ {service}: Health check failed - {e}")
                
        return results
    
    def test_swagger_docs(self) -> Dict[str, bool]:
        """Тестирование Swagger документации"""
        results = {}
        
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/swagger/", timeout=5)
                results[service] = response.status_code == 200
                print(f"✅ {service}: Swagger docs accessible")
            except requests.exceptions.RequestException as e:
                results[service] = False
                print(f"❌ {service}: Swagger docs failed - {e}")
                
        return results
    
    def test_api_gateway_proxy(self) -> Dict[str, bool]:
        """Тестирование прокси через API Gateway"""
        results = {}
        
        # Тест прокси к User Service
        try:
            response = requests.get(f"{self.base_urls['api_gateway']}/api/v1/users/", timeout=5)
            results['users_proxy'] = response.status_code in [200, 401, 403]  # 401/403 - нормально для неавторизованных запросов
            print(f"✅ API Gateway -> User Service: Proxy working")
        except requests.exceptions.RequestException as e:
            results['users_proxy'] = False
            print(f"❌ API Gateway -> User Service: Proxy failed - {e}")
        
        # Тест прокси к Zayavki Service
        try:
            response = requests.get(f"{self.base_urls['api_gateway']}/api/v1/zayavki/", timeout=5)
            results['zayavki_proxy'] = response.status_code in [200, 401, 403]
            print(f"✅ API Gateway -> Zayavki Service: Proxy working")
        except requests.exceptions.RequestException as e:
            results['zayavki_proxy'] = False
            print(f"❌ API Gateway -> Zayavki Service: Proxy failed - {e}")
        
        # Тест прокси к Finance Service
        try:
            response = requests.get(f"{self.base_urls['api_gateway']}/api/v1/finance/tranzakcii/", timeout=5)
            results['finance_proxy'] = response.status_code in [200, 401, 403]
            print(f"✅ API Gateway -> Finance Service: Proxy working")
        except requests.exceptions.RequestException as e:
            results['finance_proxy'] = False
            print(f"❌ API Gateway -> Finance Service: Proxy failed - {e}")
            
        return results
    
    def test_direct_services(self) -> Dict[str, bool]:
        """Тестирование прямого доступа к сервисам"""
        results = {}
        
        # User Service
        try:
            response = requests.get(f"{self.base_urls['user_service']}/api/v1/users/", timeout=5)
            results['user_service_direct'] = response.status_code in [200, 401, 403]
            print(f"✅ User Service: Direct access working")
        except requests.exceptions.RequestException as e:
            results['user_service_direct'] = False
            print(f"❌ User Service: Direct access failed - {e}")
        
        # Zayavki Service
        try:
            response = requests.get(f"{self.base_urls['zayavki_service']}/api/v1/zayavki/", timeout=5)
            results['zayavki_service_direct'] = response.status_code in [200, 401, 403]
            print(f"✅ Zayavki Service: Direct access working")
        except requests.exceptions.RequestException as e:
            results['zayavki_service_direct'] = False
            print(f"❌ Zayavki Service: Direct access failed - {e}")
        
        # Finance Service
        try:
            response = requests.get(f"{self.base_urls['finance_service']}/api/v1/tranzakcii/", timeout=5)
            results['finance_service_direct'] = response.status_code in [200, 401, 403]
            print(f"✅ Finance Service: Direct access working")
        except requests.exceptions.RequestException as e:
            results['finance_service_direct'] = False
            print(f"❌ Finance Service: Direct access failed - {e}")
            
        return results
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Тестирование микросервисной архитектуры CRM")
        print("=" * 60)
        
        # Ждем немного для запуска сервисов
        print("⏳ Ожидание запуска сервисов...")
        time.sleep(3)
        
        print("\n1. Тестирование Health Check:")
        health_results = self.test_health_check()
        
        print("\n2. Тестирование Swagger документации:")
        swagger_results = self.test_swagger_docs()
        
        print("\n3. Тестирование прямого доступа к сервисам:")
        direct_results = self.test_direct_services()
        
        print("\n4. Тестирование прокси через API Gateway:")
        proxy_results = self.test_api_gateway_proxy()
        
        # Сводка результатов
        print("\n" + "=" * 60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ:")
        print("=" * 60)
        
        all_results = {**health_results, **swagger_results, **direct_results, **proxy_results}
        passed = sum(all_results.values())
        total = len(all_results)
        
        print(f"✅ Успешно: {passed}/{total}")
        print(f"❌ Ошибок: {total - passed}/{total}")
        print(f"📈 Процент успеха: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("Микросервисная архитектура работает корректно.")
        else:
            print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ.")
            print("Проверьте, что все сервисы запущены.")
        
        print("\n🔗 Полезные ссылки:")
        print(f"API Gateway: {self.base_urls['api_gateway']}")
        print(f"Swagger Docs: {self.base_urls['api_gateway']}/swagger/")
        print(f"Health Check: {self.base_urls['api_gateway']}/health/")

if __name__ == "__main__":
    tester = MicroservicesTester()
    tester.run_all_tests() 