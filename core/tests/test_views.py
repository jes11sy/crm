from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, datetime, timedelta
import json
import uuid
import time
from django.utils import timezone
from django.db import models

from core.models import (
    Gorod, TipZayavki, RK, Master, TipTranzakcii, Tranzakcii,
    Roli, Polzovateli, PhoneGoroda, Zayavki, ZayavkaFile, MasterPayout
)


class BaseTestCase(APITestCase):
    """Базовый класс для тестов с общей настройкой"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаём базовые объекты
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol_admin = Roli.objects.create(name='admin')
        self.rol_master = Roli.objects.create(name='master')
        self.rol_director = Roli.objects.create(name='director')
        
        # Генерируем уникальный суффикс для каждого теста
        unique = f"{self.__class__.__name__}_{int(time.time() * 1000000)}_{str(uuid.uuid4())[:4]}"
        self.admin_user = Polzovateli.objects.create(
            name='Админ Админов',
            login=f'admin_{unique}',
            password='adminpass123',
            gorod=self.gorod,
            rol=self.rol_admin,
            is_active=True
        )
        
        self.director_user = Polzovateli.objects.create(
            name='Директор Директоров',
            login=f'director_{unique}',
            password='directorpass123',
            gorod=self.gorod,
            rol=self.rol_director,
            is_active=True
        )
        
        self.master = Master.objects.create(
            name='Иван Иванов',
            login=f'ivan_{unique}',
            password='masterpass123',
            gorod=self.gorod,
            phone='+79001234567',
            birth_date=date(1990, 1, 1),
            is_active=True
        )
        
        # Создаём связанного пользователя для мастера
        self.master_user = Polzovateli.objects.create(
            name='Иван Иванов',
            login=f'ivan_user_{unique}',
            password='masterpass123',
            gorod=self.gorod,
            rol=self.rol_master,
            is_active=True
        )


class BaseViewTest(APITestCase):
    """Базовый класс для тестов views"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем базовые данные
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        self.tip_zayavki = TipZayavki.objects.create(name='Ремонт')
        self.tip_tranzakcii = TipTranzakcii.objects.create(name='Оплата')
        
        # Создаем пользователя
        self.user = Polzovateli.objects.create(
            name='Тестовый Админ',
            login='admin',
            password='testpass123',
            gorod=self.gorod,
            rol=self.rol
        )
        
        # Создаем мастера
        self.master = Master.objects.create(
            name='Тестовый Мастер',
            phone='+79001234567',
            login='master',
            gorod=self.gorod
        )
        
        # Создаем РК
        self.rk = RK.objects.create(
            rk_name='Тестовый РК',
            gorod=self.gorod,
            phone='+79001234568'
        )
        
        # Настраиваем клиент
        self.client = APIClient()
        
        # Аутентифицируем пользователя
        self.client.force_authenticate(user=self.user)


class LoginViewTest(APITestCase):
    """Тесты для LoginView"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        
        # Создаем пользователя
        self.user = Polzovateli.objects.create(
            name='Админ',
            login='admin',
            password=make_password('admin123'),
            gorod=self.gorod,
            rol=self.rol
        )
        
        # Создаем мастера
        self.master = Master.objects.create(
            name='Мастер',
            login='master',
            phone='+79001234567',
            gorod=self.gorod
        )
    
    def test_successful_user_login(self):
        """Тест успешного входа пользователя"""
        url = reverse('login')
        data = {
            'login': 'admin',
            'password': 'admin123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['role'], 'admin')
        self.assertEqual(response.data['name'], 'Админ')
        self.assertIn('token', response.data)
        self.assertIn('jwt', response.cookies)
    
    def test_successful_master_login(self):
        """Тест успешного входа мастера"""
        url = reverse('login')
        data = {
            'login': 'master',
            'password': 'master123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['role'], 'master')
        self.assertEqual(response.data['name'], 'Мастер')
        self.assertIn('token', response.data)
        self.assertIn('jwt', response.cookies)
    
    def test_invalid_credentials(self):
        """Тест неверных учетных данных"""
        url = reverse('login')
        data = {
            'login': 'admin',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_missing_credentials(self):
        """Тест отсутствующих учетных данных"""
        url = reverse('login')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_inactive_user_login(self):
        """Тест входа неактивного пользователя"""
        self.user.is_active = False
        self.user.save()
        
        url = reverse('login')
        data = {
            'login': 'admin',
            'password': 'admin123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTest(APITestCase):
    """Тесты для LogoutView"""
    
    def test_logout(self):
        """Тест выхода из системы"""
        url = reverse('logout')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Проверяем, что cookie удален
        self.assertNotIn('jwt', response.cookies)


class MeViewTest(APITestCase):
    """Тесты для MeView"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        
        # Создаем пользователя
        self.user = Polzovateli.objects.create(
            name='Админ',
            login='admin',
            password=make_password('admin123'),
            gorod=self.gorod,
            rol=self.rol
        )
    
    def test_me_view_authenticated(self):
        """Тест получения информации о пользователе"""
        # Сначала входим в систему
        login_url = reverse('login')
        login_data = {
            'login': 'admin',
            'password': 'admin123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Получаем информацию о пользователе
        me_url = reverse('me')
        response = self.client.get(me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Админ')
        self.assertEqual(response.data['role'], 'admin')
        self.assertEqual(response.data['login'], 'admin')
        self.assertEqual(response.data['gorod_id'], self.gorod.id)
        self.assertTrue(response.data['is_active'])
    
    def test_me_view_unauthenticated(self):
        """Тест получения информации без аутентификации"""
        me_url = reverse('me')
        response = self.client.get(me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GorodViewTest(BaseViewTest):
    """Тесты для views городов"""
    
    def test_gorod_list(self):
        """Тест получения списка городов"""
        url = reverse('gorod-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Москва')
    
    def test_gorod_create(self):
        """Тест создания города"""
        url = reverse('gorod-list')
        data = {'name': 'Санкт-Петербург'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Gorod.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Санкт-Петербург')
    
    def test_gorod_detail(self):
        """Тест получения деталей города"""
        url = reverse('gorod-detail', args=[self.gorod.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Москва')
    
    def test_gorod_update(self):
        """Тест обновления города"""
        url = reverse('gorod-detail', args=[self.gorod.id])
        data = {'name': 'Новая Москва'}
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.gorod.refresh_from_db()
        self.assertEqual(self.gorod.name, 'Новая Москва')
    
    def test_gorod_delete(self):
        """Тест удаления города"""
        url = reverse('gorod-detail', args=[self.gorod.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Gorod.objects.count(), 0)


class ZayavkiViewTest(BaseViewTest):
    """Тесты для views заявок"""
    
    def setUp(self):
        super().setUp()
        # Создаем тестовую заявку
        self.zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234569',
            tip_zayavki=self.tip_zayavki,
            client_name='Тестовый Клиент',
            address='Тестовый адрес',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='Тестовый КЦ'
        )
    
    def test_zayavki_list(self):
        """Тест получения списка заявок"""
        url = reverse('zayavki-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['client_name'], 'Тестовый Клиент')
    
    def test_zayavki_create(self):
        """Тест создания заявки"""
        url = reverse('zayavki-list')
        data = {
            'rk': self.rk.id,
            'gorod': self.gorod.id,
            'phone_client': '+79001234570',
            'tip_zayavki': self.tip_zayavki.id,
            'client_name': 'Новый Клиент',
            'address': 'Новый адрес',
            'meeting_date': (timezone.now() + timedelta(days=2)).isoformat(),
            'tip_techniki': 'Стиральная машина',
            'problema': 'Не включается',
            'status': 'Ожидает',
            'master': self.master.id,
            'kc_name': 'Новый КЦ'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Zayavki.objects.count(), 2)
        self.assertEqual(response.data['client_name'], 'Новый Клиент')
    
    def test_zayavki_detail(self):
        """Тест получения деталей заявки"""
        url = reverse('zayavki-detail', args=[self.zayavka.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client_name'], 'Тестовый Клиент')
    
    def test_zayavki_update(self):
        """Тест обновления заявки"""
        url = reverse('zayavki-detail', args=[self.zayavka.id])
        data = {
            'rk': self.rk.id,
            'gorod': self.gorod.id,
            'phone_client': '+79001234569',
            'tip_zayavki': self.tip_zayavki.id,
            'client_name': 'Обновленный Клиент',
            'address': 'Обновленный адрес',
            'meeting_date': (timezone.now() + timedelta(days=1)).isoformat(),
            'tip_techniki': 'Холодильник',
            'problema': 'Не работает',
            'status': 'В работе',
            'master': self.master.id,
            'kc_name': 'Тестовый КЦ'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.zayavka.refresh_from_db()
        self.assertEqual(self.zayavka.client_name, 'Обновленный Клиент')
        self.assertEqual(self.zayavka.status, 'В работе')
    
    def test_zayavki_delete(self):
        """Тест удаления заявки"""
        url = reverse('zayavki-detail', args=[self.zayavka.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Zayavki.objects.count(), 0)
    
    def test_zayavki_filter_by_status(self):
        """Тест фильтрации заявок по статусу"""
        # Создаем еще одну заявку с другим статусом
        Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Другой Клиент',
            address='Другой адрес',
            meeting_date=timezone.now() + timedelta(days=3),
            tip_techniki='Телевизор',
            problema='Не показывает',
            status='Готово',
            master=self.master,
            kc_name='Другой КЦ'
        )
        
        url = reverse('zayavki-list')
        response = self.client.get(url, {'status': 'Ожидает'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'Ожидает')


class MasterViewTest(BaseViewTest):
    """Тесты для views мастеров"""
    
    def test_master_list(self):
        """Тест получения списка мастеров"""
        url = reverse('master-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Тестовый Мастер')
    
    def test_master_create(self):
        """Тест создания мастера"""
        url = reverse('master-list')
        data = {
            'name': 'Новый Мастер',
            'phone': '+79001234572',
            'login': 'newmaster',
            'gorod': self.gorod.id,
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Master.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Новый Мастер')
    
    def test_master_detail(self):
        """Тест получения деталей мастера"""
        url = reverse('master-detail', args=[self.master.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовый Мастер')
    
    def test_master_filter_by_city(self):
        """Тест фильтрации мастеров по городу"""
        # Создаем другой город и мастера
        gorod2 = Gorod.objects.create(name='Санкт-Петербург')
        Master.objects.create(
            name='Мастер СПб',
            phone='+79001234573',
            login='spbmaster',
            gorod=gorod2
        )
        
        url = reverse('master-list')
        response = self.client.get(url, {'gorod': self.gorod.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['gorod'], self.gorod.id)


class TranzakciiViewTest(BaseViewTest):
    """Тесты для views транзакций"""
    
    def test_tranzakcii_list(self):
        """Тест получения списка транзакций"""
        url = reverse('tranzakcii-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Пока нет транзакций
    
    def test_tranzakcii_create(self):
        """Тест создания транзакции"""
        url = reverse('tranzakcii-list')
        data = {
            'gorod': self.gorod.id,
            'tip_tranzakcii': self.tip_tranzakcii.id,
            'summa': '1000.00',
            'note': 'Тестовая транзакция'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tranzakcii.objects.count(), 1)
        self.assertEqual(response.data['summa'], '1000.00')
    
    def test_tranzakcii_sum_validation(self):
        """Тест валидации суммы транзакции"""
        url = reverse('tranzakcii-list')
        data = {
            'gorod': self.gorod.id,
            'tip_tranzakcii': self.tip_tranzakcii.id,
            'summa': '-100.00',  # Отрицательная сумма
            'note': 'Тестовая транзакция'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticationTest(TestCase):
    """Тесты аутентификации"""
    
    def setUp(self):
        self.client = Client()
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        self.user = Polzovateli.objects.create(
            name='Тестовый Пользователь',
            login='testuser',
            password='testpass123',
            gorod=self.gorod,
            rol=self.rol
        )
    
    def test_login_page(self):
        """Тест страницы входа"""
        url = reverse('login')
        response = self.client.get(url)
        
        # Проверяем, что страница доступна (может быть редирект на логин)
        self.assertIn(response.status_code, [200, 302])
    
    def test_logout_redirect(self):
        """Тест выхода из системы"""
        url = reverse('logout')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Редирект


class HealthCheckTest(APITestCase):
    """Тесты для health check"""
    
    def test_health_check(self):
        """Тест health check endpoint"""
        url = reverse('health')
        response = self.client.get(url)
        
        # Health check должен быть доступен без аутентификации
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'healthy')


class ModelCRUDTest(BaseViewTest):
    """Тесты CRUD операций для моделей"""
    
    def test_gorod_crud(self):
        """Тест CRUD операций для городов"""
        # Создание
        gorod = Gorod.objects.create(name='Санкт-Петербург')
        self.assertEqual(gorod.name, 'Санкт-Петербург')
        
        # Чтение
        gorod_from_db = Gorod.objects.get(id=gorod.id)
        self.assertEqual(gorod_from_db.name, 'Санкт-Петербург')
        
        # Обновление
        gorod.name = 'Новый Санкт-Петербург'
        gorod.save()
        gorod.refresh_from_db()
        self.assertEqual(gorod.name, 'Новый Санкт-Петербург')
        
        # Удаление
        gorod_id = gorod.id
        gorod.delete()
        self.assertFalse(Gorod.objects.filter(id=gorod_id).exists())
    
    def test_master_crud(self):
        """Тест CRUD операций для мастеров"""
        # Создание
        master = Master.objects.create(
            name='Новый Мастер',
            phone='+79001234570',
            login='newmaster',
            gorod=self.gorod
        )
        self.assertEqual(master.name, 'Новый Мастер')
        
        # Чтение
        master_from_db = Master.objects.get(id=master.id)
        self.assertEqual(master_from_db.name, 'Новый Мастер')
        
        # Обновление
        master.name = 'Обновленный Мастер'
        master.save()
        master.refresh_from_db()
        self.assertEqual(master.name, 'Обновленный Мастер')
        
        # Удаление
        master_id = master.id
        master.delete()
        self.assertFalse(Master.objects.filter(id=master_id).exists())
    
    def test_zayavki_crud(self):
        """Тест CRUD операций для заявок"""
        # Создание
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Тестовый Клиент',
            address='Тестовый адрес',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='Тестовый КЦ'
        )
        self.assertEqual(zayavka.client_name, 'Тестовый Клиент')
        
        # Чтение
        zayavka_from_db = Zayavki.objects.get(id=zayavka.id)
        self.assertEqual(zayavka_from_db.client_name, 'Тестовый Клиент')
        
        # Обновление
        zayavka.status = 'В работе'
        zayavka.save()
        zayavka.refresh_from_db()
        self.assertEqual(zayavka.status, 'В работе')
        
        # Удаление
        zayavka_id = zayavka.id
        zayavka.delete()
        self.assertFalse(Zayavki.objects.filter(id=zayavka_id).exists())
    
    def test_tranzakcii_crud(self):
        """Тест CRUD операций для транзакций"""
        # Создание
        tranzakciya = Tranzakcii.objects.create(
            gorod=self.gorod,
            tip_tranzakcii=self.tip_tranzakcii,
            summa=1000.00,
            note='Тестовая транзакция'
        )
        self.assertEqual(tranzakciya.summa, 1000.00)
        
        # Чтение
        tranzakciya_from_db = Tranzakcii.objects.get(id=tranzakciya.id)
        self.assertEqual(tranzakciya_from_db.summa, 1000.00)
        
        # Обновление
        tranzakciya.summa = 1500.00
        tranzakciya.save()
        tranzakciya.refresh_from_db()
        self.assertEqual(tranzakciya.summa, 1500.00)
        
        # Удаление
        tranzakciya_id = tranzakciya.id
        tranzakciya.delete()
        self.assertFalse(Tranzakcii.objects.filter(id=tranzakciya_id).exists())


class ValidationTest(BaseViewTest):
    """Тесты валидации данных"""
    
    def test_phone_validation(self):
        """Тест валидации номера телефона"""
        # Валидный номер
        master = Master.objects.create(
            name='Тест',
            phone='+79001234567',
            login='test',
            gorod=self.gorod
        )
        self.assertEqual(master.phone, '+79001234567')
        
        # Невалидный номер должен вызвать ошибку
        with self.assertRaises(Exception):
            Master.objects.create(
                name='Тест2',
                phone='invalid_phone',
                login='test2',
                gorod=self.gorod
            )
    
    def test_unique_constraints(self):
        """Тест уникальных ограничений"""
        # Создаем первый город
        Gorod.objects.create(name='Уникальный город')
        
        # Попытка создать город с тем же именем должна вызвать ошибку
        with self.assertRaises(Exception):
            Gorod.objects.create(name='Уникальный город')
    
    def test_required_fields(self):
        """Тест обязательных полей"""
        # Попытка создать заявку без обязательных полей должна вызвать ошибку
        with self.assertRaises(Exception):
            Zayavki.objects.create(
                # Не указываем обязательные поля
            )


class BusinessLogicTest(BaseViewTest):
    """Тесты бизнес-логики"""
    
    def test_zayavki_calculations(self):
        """Тест автоматических расчетов в заявках"""
        # Создаем заявку без итога и расхода
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Тестовый Клиент',
            address='Тестовый адрес',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='Тестовый КЦ'
        )
        # Добавляем итог и расход, сохраняем
        zayavka.itog = Decimal('1000.00')
        zayavka.rashod = Decimal('200.00')
        zayavka.save()
        zayavka.refresh_from_db()
        # Проверяем расчет до смены статуса
        self.assertEqual(zayavka.chistymi, Decimal('800.00'))
        self.assertEqual(zayavka.sdacha_mastera, Decimal('400.00'))

    def test_master_payout_creation(self):
        """Тест автоматического создания выплаты при завершении заявки"""
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Тестовый Клиент',
            address='Тестовый адрес',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='Тестовый КЦ',
        )
        zayavka.itog = Decimal('1000.00')
        zayavka.rashod = Decimal('200.00')
        zayavka.save()
        # Меняем статус на "Готово"
        zayavka.status = 'Готово'
        zayavka.save()
        zayavka.refresh_from_db()
        # Проверяем, что выплата была создана
        self.assertTrue(hasattr(zayavka, 'payout'))
        self.assertEqual(zayavka.payout.summa, Decimal('400.00'))  # sdacha_mastera


class SearchAndFilterTest(BaseViewTest):
    """Тесты поиска и фильтрации"""
    
    def setUp(self):
        super().setUp()
        # Создаем тестовые данные
        self.zayavka1 = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Иван Петров',
            address='ул. Ленина, 1',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='КЦ 1'
        )
        
        self.zayavka2 = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234572',
            tip_zayavki=self.tip_zayavki,
            client_name='Петр Сидоров',
            address='ул. Пушкина, 10',
            meeting_date=timezone.now() + timedelta(days=2),
            tip_techniki='Стиральная машина',
            problema='Не включается',
            status='В работе',
            master=self.master,
            kc_name='КЦ 2'
        )
    
    def test_filter_by_status(self):
        """Тест фильтрации по статусу"""
        # Фильтруем по статусу "Ожидает"
        zayavki_ozhidayut = Zayavki.objects.filter(status='Ожидает')
        self.assertEqual(zayavki_ozhidayut.count(), 1)
        self.assertEqual(zayavki_ozhidayut.first().client_name, 'Иван Петров')
        
        # Фильтруем по статусу "В работе"
        zayavki_v_rabote = Zayavki.objects.filter(status='В работе')
        self.assertEqual(zayavki_v_rabote.count(), 1)
        self.assertEqual(zayavki_v_rabote.first().client_name, 'Петр Сидоров')
    
    def test_search_by_client_name(self):
        """Тест поиска по имени клиента"""
        # Поиск по части имени
        zayavki_ivan = Zayavki.objects.filter(client_name__icontains='Иван')
        self.assertEqual(zayavki_ivan.count(), 1)
        self.assertEqual(zayavki_ivan.first().client_name, 'Иван Петров')
    
    def test_search_by_address(self):
        """Тест поиска по адресу"""
        # Поиск по части адреса
        zayavki_lenina = Zayavki.objects.filter(address__icontains='Ленина')
        self.assertEqual(zayavki_lenina.count(), 1)
        self.assertEqual(zayavki_lenina.first().address, 'ул. Ленина, 1')
    
    def test_filter_by_master(self):
        """Тест фильтрации по мастеру"""
        # Фильтруем по мастеру
        zayavki_mastera = Zayavki.objects.filter(master=self.master)
        self.assertEqual(zayavki_mastera.count(), 2)
    
    def test_filter_by_city(self):
        """Тест фильтрации по городу"""
        # Создаем другой город и заявку
        gorod2 = Gorod.objects.create(name='Санкт-Петербург')
        Zayavki.objects.create(
            rk=self.rk,
            gorod=gorod2,
            phone_client='+79001234573',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент СПб',
            address='Невский проспект, 1',
            meeting_date=timezone.now() + timedelta(days=3),
            tip_techniki='Телевизор',
            problema='Не показывает',
            status='Ожидает',
            master=self.master,
            kc_name='КЦ СПб'
        )
        
        # Фильтруем по городу Москва
        zayavki_moskva = Zayavki.objects.filter(gorod=self.gorod)
        self.assertEqual(zayavki_moskva.count(), 2)
        
        # Фильтруем по городу СПб
        zayavki_spb = Zayavki.objects.filter(gorod=gorod2)
        self.assertEqual(zayavki_spb.count(), 1)


class StatisticsTest(BaseViewTest):
    """Тесты статистики"""
    
    def setUp(self):
        super().setUp()
        # Создаем тестовые данные для статистики
        self.zayavka1 = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент 1',
            address='Адрес 1',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Проблема 1',
            status='Готово',
            master=self.master,
            kc_name='КЦ 1',
            itog=1000.00,
            rashod=200.00
        )
        
        self.zayavka2 = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234572',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент 2',
            address='Адрес 2',
            meeting_date=timezone.now() + timedelta(days=2),
            tip_techniki='Стиральная машина',
            problema='Проблема 2',
            status='Ожидает',
            master=self.master,
            kc_name='КЦ 2'
        )
    
    def test_zayavki_statistics(self):
        """Тест статистики заявок"""
        # Общее количество заявок
        total_zayavki = Zayavki.objects.count()
        self.assertEqual(total_zayavki, 2)
        
        # Заявки по статусам
        zayavki_gotovo = Zayavki.objects.filter(status='Готово').count()
        self.assertEqual(zayavki_gotovo, 1)
        
        zayavki_ozhidayut = Zayavki.objects.filter(status='Ожидает').count()
        self.assertEqual(zayavki_ozhidayut, 1)
    
    def test_finance_statistics(self):
        """Тест финансовой статистики"""
        # Общая выручка
        total_revenue = Zayavki.objects.aggregate(
            total=models.Sum('itog')
        )['total'] or 0
        self.assertEqual(total_revenue, 1000.00)
        
        # Общие расходы
        total_expenses = Zayavki.objects.aggregate(
            total=models.Sum('rashod')
        )['total'] or 0
        self.assertEqual(total_expenses, 200.00)
        
        # Прибыль
        profit = total_revenue - total_expenses
        self.assertEqual(profit, 800.00)
    
    def test_master_statistics(self):
        """Тест статистики по мастерам"""
        # Количество заявок у мастера
        master_zayavki = Zayavki.objects.filter(master=self.master).count()
        self.assertEqual(master_zayavki, 2)
        
        # Выручка мастера
        master_revenue = Zayavki.objects.filter(master=self.master).aggregate(
            total=models.Sum('itog')
        )['total'] or 0
        self.assertEqual(master_revenue, 1000.00)


class FileHandlingTest(BaseViewTest):
    """Тесты обработки файлов"""
    
    def setUp(self):
        super().setUp()
        self.zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Тестовый Клиент',
            address='Тестовый адрес',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='Тестовый КЦ'
        )
    
    def test_zayavka_file_creation(self):
        """Тест создания файла заявки"""
        # Создаем файл заявки
        zayavka_file = ZayavkaFile.objects.create(
            zayavka=self.zayavka,
            type='bso',
            uploaded_by=self.user
        )
        
        self.assertEqual(zayavka_file.zayavka, self.zayavka)
        self.assertEqual(zayavka_file.type, 'bso')
        self.assertEqual(zayavka_file.uploaded_by, self.user)
    
    def test_file_type_validation(self):
        """Тест валидации типа файла"""
        # Создаем файл с валидным типом
        zayavka_file = ZayavkaFile.objects.create(
            zayavka=self.zayavka,
            type='audio',
            uploaded_by=self.user
        )
        self.assertEqual(zayavka_file.type, 'audio')
        
        # Попытка создать файл с невалидным типом должна вызвать ошибку
        with self.assertRaises(Exception):
            ZayavkaFile.objects.create(
                zayavka=self.zayavka,
                type='invalid_type',
                uploaded_by=self.user
            )


class IntegrationTest(BaseViewTest):
    """Интеграционные тесты"""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # 1. Создаем заявку
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент',
            address='Адрес',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='КЦ'
        )
        
        # 2. Назначаем мастера и меняем статус
        zayavka.status = 'В работе'
        zayavka.save()
        
        # 3. Завершаем работу
        zayavka.status = 'Готово'
        zayavka.itog = Decimal('1000.00')
        zayavka.rashod = Decimal('200.00')
        zayavka.save()
        
        # 4. Проверяем автоматические расчеты
        self.assertEqual(zayavka.chistymi, Decimal('800.00'))
        self.assertEqual(zayavka.sdacha_mastera, Decimal('400.00'))
        
        # 5. Проверяем создание выплаты
        self.assertTrue(hasattr(zayavka, 'payout'))
        self.assertEqual(zayavka.payout.summa, Decimal('400.00'))
        self.assertEqual(zayavka.payout.status, 'pending')
    
    def test_data_consistency(self):
        """Тест согласованности данных"""
        # Создаем заявку
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234571',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент',
            address='Адрес',
            meeting_date=timezone.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            status='Ожидает',
            master=self.master,
            kc_name='КЦ'
        )
        
        # Проверяем связи
        self.assertEqual(zayavka.rk.gorod, self.gorod)
        self.assertEqual(zayavka.master.gorod, self.gorod)
        self.assertEqual(zayavka.tip_zayavki.name, 'Ремонт')
        
        # Проверяем, что все связанные объекты существуют
        self.assertTrue(RK.objects.filter(id=self.rk.id).exists())
        self.assertTrue(Master.objects.filter(id=self.master.id).exists())
        self.assertTrue(TipZayavki.objects.filter(id=self.tip_zayavki.id).exists()) 