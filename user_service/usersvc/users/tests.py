"""
Тесты для микросервиса пользователей
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import Gorod, Roli, Polzovateli, Master


class GorodModelTest(TestCase):
    """Тесты модели города"""
    
    def test_gorod_creation(self):
        """Тест создания города"""
        gorod = Gorod.objects.create(name='Москва')
        self.assertEqual(gorod.name, 'Москва')
        self.assertEqual(str(gorod), 'Москва')
    
    def test_gorod_unique_name(self):
        """Тест уникальности названия города"""
        Gorod.objects.create(name='Санкт-Петербург')
        with self.assertRaises(Exception):
            Gorod.objects.create(name='Санкт-Петербург')


class RoliModelTest(TestCase):
    """Тесты модели роли"""
    
    def test_roli_creation(self):
        """Тест создания роли"""
        rol = Roli.objects.create(name='admin')
        self.assertEqual(rol.name, 'admin')
        self.assertEqual(str(rol), 'admin')
    
    def test_roli_unique_name(self):
        """Тест уникальности названия роли"""
        Roli.objects.create(name='user')
        with self.assertRaises(Exception):
            Roli.objects.create(name='user')


class PolzovateliModelTest(TestCase):
    """Тесты модели пользователя"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
    
    def test_polzovateli_creation(self):
        """Тест создания пользователя"""
        user = Polzovateli.objects.create(
            gorod=self.gorod,
            name='Тестовый пользователь',
            rol=self.rol,
            login='testuser',
            password='testpass123'
        )
        self.assertEqual(user.name, 'Тестовый пользователь')
        self.assertEqual(user.login, 'testuser')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_polzovateli_str(self):
        """Тест строкового представления пользователя"""
        user = Polzovateli.objects.create(
            gorod=self.gorod,
            name='Тестовый пользователь',
            rol=self.rol,
            login='testuser',
            password='testpass123'
        )
        self.assertEqual(str(user), 'Тестовый пользователь (testuser)')


class MasterModelTest(TestCase):
    """Тесты модели мастера"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
    
    def test_master_creation(self):
        """Тест создания мастера"""
        master = Master.objects.create(
            gorod=self.gorod,
            name='Тестовый мастер',
            phone='+79001234567',
            login='master1',
            password='masterpass123'
        )
        self.assertEqual(master.name, 'Тестовый мастер')
        self.assertEqual(master.phone, '+79001234567')
        self.assertEqual(master.login, 'master1')
    
    def test_master_str(self):
        """Тест строкового представления мастера"""
        master = Master.objects.create(
            gorod=self.gorod,
            name='Тестовый мастер',
            phone='+79001234567',
            login='master1',
            password='masterpass123'
        )
        self.assertEqual(str(master), 'Тестовый мастер (Москва)')


class GorodAPITest(APITestCase):
    """Тесты API для городов"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = APIClient()
        self.gorod = Gorod.objects.create(name='Москва')
    
    def test_get_gorod_list(self):
        """Тест получения списка городов"""
        url = reverse('gorod-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Москва')
    
    def test_create_gorod(self):
        """Тест создания города"""
        url = reverse('gorod-list')
        data = {'name': 'Санкт-Петербург'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Gorod.objects.count(), 2)
    
    def test_get_gorod_detail(self):
        """Тест получения деталей города"""
        url = reverse('gorod-detail', args=[self.gorod.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Москва')


class PolzovateliAPITest(APITestCase):
    """Тесты API для пользователей"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = APIClient()
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        self.user = Polzovateli.objects.create(
            gorod=self.gorod,
            name='Тестовый пользователь',
            rol=self.rol,
            login='testuser',
            password='testpass123'
        )
    
    def test_get_polzovateli_list(self):
        """Тест получения списка пользователей"""
        url = reverse('polzovateli-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_polzovateli(self):
        """Тест создания пользователя"""
        url = reverse('polzovateli-list')
        data = {
            'name': 'Новый пользователь',
            'login': 'newuser',
            'password': 'newpass123',
            'gorod_id': self.gorod.id,
            'rol_id': self.rol.id,
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Polzovateli.objects.count(), 2)
    
    def test_authenticate_user(self):
        """Тест аутентификации пользователя"""
        url = reverse('polzovateli-authenticate')
        data = {
            'login': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
    
    def test_authenticate_invalid_credentials(self):
        """Тест аутентификации с неверными данными"""
        url = reverse('polzovateli-authenticate')
        data = {
            'login': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MasterAPITest(APITestCase):
    """Тесты API для мастеров"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = APIClient()
        self.gorod = Gorod.objects.create(name='Москва')
        self.master = Master.objects.create(
            gorod=self.gorod,
            name='Тестовый мастер',
            phone='+79001234567',
            login='master1',
            password='masterpass123'
        )
    
    def test_get_master_list(self):
        """Тест получения списка мастеров"""
        url = reverse('master-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_master(self):
        """Тест создания мастера"""
        url = reverse('master-list')
        data = {
            'name': 'Новый мастер',
            'phone': '+79009876543',
            'login': 'master2',
            'password': 'newmasterpass123',
            'gorod_id': self.gorod.id,
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Master.objects.count(), 2)
    
    def test_authenticate_master(self):
        """Тест аутентификации мастера"""
        url = reverse('master-authenticate')
        data = {
            'login': 'master1',
            'password': 'masterpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
