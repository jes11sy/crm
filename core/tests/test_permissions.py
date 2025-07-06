from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date
import uuid
import time
from django.urls import reverse

from core.models import (
    Gorod, TipZayavki, RK, Master, TipTranzakcii, Tranzakcii,
    Roli, Polzovateli, PhoneGoroda, Zayavki, ZayavkaFile, MasterPayout
)
from core.permissions import (
    IsDirectorOrAdmin, IsMasterOrAbove, IsKCUserOrAbove, 
    IsSameCity, IsOwnerOrSameCity, IsReadOnlyForKC,
    IsMasterOrDirectorForMasterData, IsAdminOnly, IsDirectorOrAdminForFinancial,
    IsCallCentreOrAbove
)


class BasePermissionTestCase(APITestCase):
    """Базовый класс для тестов permissions"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаём или получаем город
        self.gorod_moscow, _ = Gorod.objects.get_or_create(name='Москва')
        self.gorod_spb, _ = Gorod.objects.get_or_create(name='Санкт-Петербург')
        
        # Создаём или получаем роли
        self.rol_admin, _ = Roli.objects.get_or_create(name='admin')
        self.rol_director, _ = Roli.objects.get_or_create(name='director')
        self.rol_master, _ = Roli.objects.get_or_create(name='master')
        self.rol_kc, _ = Roli.objects.get_or_create(name='kc')
        self.rol_callcentre, _ = Roli.objects.get_or_create(name='callcentre')
        
        # Генерируем уникальный суффикс для каждого теста
        unique = f"{self.__class__.__name__}_{int(time.time() * 1000000)}_{str(uuid.uuid4())[:4]}"
        # Ограничиваем длину login до 45 символов
        def short_login(prefix):
            base = f"{prefix}_{unique}"
            return base[:45]
        self.admin_user = Polzovateli.objects.create(
            name='Админ Админов',
            login=short_login('admin'),
            password=make_password('adminpass123'),
            gorod=self.gorod_moscow,
            rol=self.rol_admin,
            is_active=True
        )
        
        self.director_user = Polzovateli.objects.create(
            name='Директор Директоров',
            login=short_login('director'),
            password=make_password('directorpass123'),
            gorod=self.gorod_moscow,
            rol=self.rol_director,
            is_active=True
        )
        
        self.kc_user = Polzovateli.objects.create(
            name='КЦ Пользователь',
            login=short_login('kc'),
            password=make_password('kcpass123'),
            gorod=self.gorod_moscow,
            rol=self.rol_kc,
            is_active=True
        )
        
        self.callcentre_user = Polzovateli.objects.create(
            name='Колл-центр',
            login=short_login('callcentre'),
            password=make_password('callcentrepass123'),
            gorod=self.gorod_moscow,
            rol=self.rol_callcentre,
            is_active=True
        )
        
        # Создаём мастеров
        self.master_moscow = Master.objects.create(
            name='Иван Иванов',
            login=short_login('ivan'),
            password=make_password('masterpass123'),
            gorod=self.gorod_moscow,
            phone='+79001234567',
            birth_date=date(1990, 1, 1),
            is_active=True
        )
        
        self.master_spb = Master.objects.create(
            name='Петр Петров',
            login=short_login('petr'),
            password=make_password('masterpass123'),
            gorod=self.gorod_spb,
            phone='+79001234568',
            birth_date=date(1995, 5, 15),
            is_active=True
        )
        
        # Создаём связанных пользователей для мастеров
        self.master_user_moscow = Polzovateli.objects.create(
            name='Иван Иванов',
            login=short_login('ivan_user'),
            password=make_password('masterpass123'),
            gorod=self.gorod_moscow,
            rol=self.rol_master,
            is_active=True
        )
        
        self.master_user_spb = Polzovateli.objects.create(
            name='Петр Петров',
            login=short_login('petr_user'),
            password=make_password('masterpass123'),
            gorod=self.gorod_spb,
            rol=self.rol_master,
            is_active=True
        )


class IsDirectorOrAdminPermissionTest(BasePermissionTestCase):
    """Тесты для IsDirectorOrAdmin permission"""
    
    def test_admin_has_permission(self):
        """Тест доступа администратора"""
        permission = IsDirectorOrAdmin()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_has_permission(self):
        """Тест доступа директора"""
        permission = IsDirectorOrAdmin()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_master_no_permission(self):
        """Тест отсутствия доступа у мастера"""
        permission = IsDirectorOrAdmin()
        request = type('Request', (), {'user': self.master_user_moscow})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))
    
    def test_kc_no_permission(self):
        """Тест отсутствия доступа у КЦ пользователя"""
        permission = IsDirectorOrAdmin()
        request = type('Request', (), {'user': self.kc_user})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))


class IsMasterOrAbovePermissionTest(BasePermissionTestCase):
    """Тесты для IsMasterOrAbove permission"""
    
    def test_admin_has_permission(self):
        """Тест доступа администратора"""
        permission = IsMasterOrAbove()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_has_permission(self):
        """Тест доступа директора"""
        permission = IsMasterOrAbove()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_master_has_permission(self):
        """Тест доступа мастера"""
        permission = IsMasterOrAbove()
        request = type('Request', (), {'user': self.master_user_moscow})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_kc_no_permission(self):
        """Тест отсутствия доступа у КЦ пользователя"""
        permission = IsMasterOrAbove()
        request = type('Request', (), {'user': self.kc_user})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))


class IsKCUserOrAbovePermissionTest(BasePermissionTestCase):
    """Тесты для IsKCUserOrAbove permission"""
    
    def test_admin_has_permission(self):
        """Тест доступа администратора"""
        permission = IsKCUserOrAbove()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_has_permission(self):
        """Тест доступа директора"""
        permission = IsKCUserOrAbove()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_kc_has_permission(self):
        """Тест доступа КЦ пользователя"""
        permission = IsKCUserOrAbove()
        request = type('Request', (), {'user': self.kc_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_callcentre_no_permission(self):
        """Тест отсутствия доступа у колл-центра"""
        permission = IsKCUserOrAbove()
        request = type('Request', (), {'user': self.callcentre_user})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))


class IsCallCentreOrAbovePermissionTest(BasePermissionTestCase):
    """Тесты для IsCallCentreOrAbove permission"""
    
    def test_admin_has_permission(self):
        """Тест доступа администратора"""
        permission = IsCallCentreOrAbove()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_has_permission(self):
        """Тест доступа директора"""
        permission = IsCallCentreOrAbove()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_kc_has_permission(self):
        """Тест доступа КЦ пользователя"""
        permission = IsCallCentreOrAbove()
        request = type('Request', (), {'user': self.kc_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_callcentre_has_permission(self):
        """Тест доступа колл-центра"""
        permission = IsCallCentreOrAbove()
        request = type('Request', (), {'user': self.callcentre_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))


class IsSameCityPermissionTest(BasePermissionTestCase):
    """Тесты для IsSameCity permission"""
    
    def setUp(self):
        super().setUp()
        # Создаём объекты для тестирования
        self.rk_moscow = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod_moscow,
            phone='+79001234567'
        )
        self.rk_spb = RK.objects.create(
            rk_name='РК СПб',
            gorod=self.gorod_spb,
            phone='+79001234568'
        )
    
    def test_same_city_access(self):
        """Тест доступа к объектам своего города"""
        permission = IsSameCity()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {'get_object': lambda: self.rk_moscow})()
        
        self.assertTrue(permission.has_object_permission(request, view, self.rk_moscow))
    
    def test_different_city_no_access(self):
        """Тест отсутствия доступа к объектам другого города"""
        permission = IsSameCity()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {'get_object': lambda: self.rk_spb})()
        
        self.assertFalse(permission.has_object_permission(request, view, self.rk_spb))
    
    def test_admin_has_all_access(self):
        """Тест доступа администратора ко всем городам"""
        permission = IsSameCity()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {'get_object': lambda: self.rk_spb})()
        
        self.assertTrue(permission.has_object_permission(request, view, self.rk_spb))


class IsOwnerOrSameCityPermissionTest(BasePermissionTestCase):
    """Тесты для IsOwnerOrSameCity permission"""
    
    def setUp(self):
        super().setUp()
        # Создаём заявки
        self.tip_zayavki = TipZayavki.objects.create(name='Ремонт холодильника')
        self.rk_moscow = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod_moscow,
            phone='+79001234567'
        )
        
        self.zayavka_moscow = Zayavki.objects.create(
            gorod=self.gorod_moscow,
            master=self.master_moscow,
            rk=self.rk_moscow,
            tip_zayavki=self.tip_zayavki,
            phone_client='+79001234567',
            client_name='Клиент Москва',
            status='Новая',
            meeting_date='2024-01-15'
        )
        
        self.zayavka_spb = Zayavki.objects.create(
            gorod=self.gorod_spb,
            master=self.master_spb,
            rk=self.rk_moscow,  # Используем тот же РК для простоты
            tip_zayavki=self.tip_zayavki,
            phone_client='+79001234568',
            client_name='Клиент СПб',
            status='Новая',
            meeting_date='2024-01-16'
        )
    
    def test_owner_has_access(self):
        """Тест доступа владельца заявки"""
        permission = IsOwnerOrSameCity()
        request = type('Request', (), {'user': self.master_user_moscow})()
        view = type('View', (), {'get_object': lambda: self.zayavka_moscow})()
        
        self.assertTrue(permission.has_object_permission(request, view, self.zayavka_moscow))
    
    def test_same_city_access(self):
        """Тест доступа пользователя того же города"""
        permission = IsOwnerOrSameCity()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {'get_object': lambda: self.zayavka_moscow})()
        
        self.assertTrue(permission.has_object_permission(request, view, self.zayavka_moscow))
    
    def test_different_city_no_access(self):
        """Тест отсутствия доступа к заявке другого города"""
        permission = IsOwnerOrSameCity()
        request = type('Request', (), {'user': self.master_user_moscow})()
        view = type('View', (), {'get_object': lambda: self.zayavka_spb})()
        
        self.assertFalse(permission.has_object_permission(request, view, self.zayavka_spb))


class IsAdminOnlyPermissionTest(BasePermissionTestCase):
    """Тесты для IsAdminOnly permission"""
    
    def test_admin_has_permission(self):
        """Тест доступа администратора"""
        permission = IsAdminOnly()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_no_permission(self):
        """Тест отсутствия доступа у директора"""
        permission = IsAdminOnly()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))
    
    def test_master_no_permission(self):
        """Тест отсутствия доступа у мастера"""
        permission = IsAdminOnly()
        request = type('Request', (), {'user': self.master_user_moscow})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))


class IsDirectorOrAdminForFinancialPermissionTest(BasePermissionTestCase):
    """Тесты для IsDirectorOrAdminForFinancial permission"""
    
    def test_admin_has_permission(self):
        """Тест доступа администратора"""
        permission = IsDirectorOrAdminForFinancial()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_has_permission(self):
        """Тест доступа директора"""
        permission = IsDirectorOrAdminForFinancial()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_master_no_permission(self):
        """Тест отсутствия доступа у мастера"""
        permission = IsDirectorOrAdminForFinancial()
        request = type('Request', (), {'user': self.master_user_moscow})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))


class IsMasterOrDirectorForMasterDataPermissionTest(BasePermissionTestCase):
    """Тесты для IsMasterOrDirectorForMasterData permission"""
    
    def test_admin_has_permission(self):
        """Тест доступа администратора"""
        permission = IsMasterOrDirectorForMasterData()
        request = type('Request', (), {'user': self.admin_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_has_permission(self):
        """Тест доступа директора"""
        permission = IsMasterOrDirectorForMasterData()
        request = type('Request', (), {'user': self.director_user})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_master_has_permission(self):
        """Тест доступа мастера"""
        permission = IsMasterOrDirectorForMasterData()
        request = type('Request', (), {'user': self.master_user_moscow})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_kc_no_permission(self):
        """Тест отсутствия доступа у КЦ пользователя"""
        permission = IsMasterOrDirectorForMasterData()
        request = type('Request', (), {'user': self.kc_user})()
        view = type('View', (), {})()
        
        self.assertFalse(permission.has_permission(request, view))


class IsReadOnlyForKCPermissionTest(BasePermissionTestCase):
    """Тесты для IsReadOnlyForKC permission"""
    
    def test_admin_full_access(self):
        """Тест полного доступа администратора"""
        permission = IsReadOnlyForKC()
        request = type('Request', (), {'user': self.admin_user, 'method': 'POST'})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_director_full_access(self):
        """Тест полного доступа директора"""
        permission = IsReadOnlyForKC()
        request = type('Request', (), {'user': self.director_user, 'method': 'PUT'})()
        view = type('View', (), {})()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_kc_read_only_access(self):
        """Тест доступа только для чтения у КЦ пользователя"""
        permission = IsReadOnlyForKC()
        
        # GET запрос разрешен
        request = type('Request', (), {'user': self.kc_user, 'method': 'GET'})()
        view = type('View', (), {})()
        self.assertTrue(permission.has_permission(request, view))
        
        # POST запрос запрещен
        request = type('Request', (), {'user': self.kc_user, 'method': 'POST'})()
        self.assertFalse(permission.has_permission(request, view))
        
        # PUT запрос запрещен
        request = type('Request', (), {'user': self.kc_user, 'method': 'PUT'})()
        self.assertFalse(permission.has_permission(request, view))
        
        # DELETE запрос запрещен
        request = type('Request', (), {'user': self.kc_user, 'method': 'DELETE'})()
        self.assertFalse(permission.has_permission(request, view))


class PermissionIntegrationTest(BasePermissionTestCase):
    """Интеграционные тесты permissions с реальными API endpoints"""
    
    def setUp(self):
        super().setUp()
        login_url = reverse('login')
        # Используем логин из базового setUp (self.admin_user.login)
        login_data = {'login': self.admin_user.login, 'password': 'adminpass123'}
        
        # Отладочная информация
        print(f"Используем логин: {self.admin_user.login}")
        print(f"Пароль: {login_data['password']}")
        print(f"Пользователь существует: {Polzovateli.objects.filter(login=self.admin_user.login).exists()}")
        
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Проверяем, что авторизация прошла успешно
        print(f"Статус ответа: {login_response.status_code}")
        print(f"Ответ: {login_response.data}")
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Получаем JWT токен из cookies
        if 'jwt' in login_response.cookies:
            self.admin_jwt = login_response.cookies['jwt'].value
        else:
            # Если токен не в cookies, берем из response body
            self.admin_jwt = login_response.data.get('token')
        
        self.assertIsNotNone(self.admin_jwt, "JWT токен не получен")
    
    def test_gorod_endpoint_permissions(self):
        """Тест permissions для endpoints городов"""
        url = reverse('gorod-list')
        
        # Админ имеет доступ
        self.client.cookies['jwt'] = self.admin_jwt
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Авторизуемся как КЦ пользователь
        login_url = reverse('login')
        login_data = {'login': 'callcentre', 'password': 'callcentrepass123'}
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Получаем JWT токен
        if 'jwt' in login_response.cookies:
            callcentre_jwt = login_response.cookies['jwt'].value
        else:
            callcentre_jwt = login_response.data.get('token')
        
        self.client.cookies['jwt'] = callcentre_jwt
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # КЦ может читать города
        
        # Но не может создавать
        data = {'name': 'Новый город'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_master_endpoint_permissions(self):
        """Тест permissions для endpoints мастеров"""
        url = reverse('master-list')
        
        # Админ имеет полный доступ
        self.client.cookies['jwt'] = self.admin_jwt
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Авторизуемся как мастер
        login_url = reverse('login')
        login_data = {'login': 'ivan', 'password': 'masterpass123'}
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Получаем JWT токен
        if 'jwt' in login_response.cookies:
            master_jwt = login_response.cookies['jwt'].value
        else:
            master_jwt = login_response.data.get('token')
        
        self.client.cookies['jwt'] = master_jwt
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Мастер может видеть мастеров
        
        # Но не может создавать новых мастеров
        data = {
            'name': 'Новый мастер',
            'login': 'newmaster',
            'password': 'newpass123',
            'gorod': self.gorod_moscow.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_zayavki_endpoint_permissions(self):
        """Тест permissions для endpoints заявок"""
        # Создаём тестовую заявку
        tip_zayavki = TipZayavki.objects.create(name='Ремонт холодильника')
        rk = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod_moscow,
            phone='+79001234567'
        )
        
        zayavka = Zayavki.objects.create(
            gorod=self.gorod_moscow,
            master=self.master_moscow,
            rk=rk,
            tip_zayavki=tip_zayavki,
            phone_client='+79001234567',
            client_name='Клиент',
            status='Новая',
            meeting_date='2024-01-17'
        )
        
        url = reverse('zayavki-list')
        
        # Админ имеет полный доступ
        self.client.cookies['jwt'] = self.admin_jwt
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Авторизуемся как мастер
        login_url = reverse('login')
        login_data = {'login': 'ivan', 'password': 'masterpass123'}
        login_response = self.client.post(login_url, login_data, format='json')
        
        # Получаем JWT токен
        if 'jwt' in login_response.cookies:
            master_jwt = login_response.cookies['jwt'].value
        else:
            master_jwt = login_response.data.get('token')
        
        self.client.cookies['jwt'] = master_jwt
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Мастер может видеть заявки
        
        # Мастер может обновлять свои заявки
        detail_url = reverse('zayavki-detail', args=[zayavka.id])
        data = {
            'gorod': self.gorod_moscow.id,
            'master': self.master_moscow.id,
            'rk': rk.id,
            'tip_zayavki': tip_zayavki.id,
            'phone_client': '+79001234567',
            'client_name': 'Клиент',
            'status': 'В работе'
        }
        response = self.client.put(detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 