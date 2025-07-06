from django.test import TestCase
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
import jwt
from unittest.mock import patch, MagicMock

from core.models import (
    Gorod, TipZayavki, RK, Master, TipTranzakcii, Tranzakcii,
    Roli, Polzovateli, PhoneGoroda, Zayavki, ZayavkaFile, MasterPayout
)
from core.utils import (
    custom_exception_handler, download_audio_for_zayavka,
    send_telegram_message, get_user_from_token, get_master_from_token
)
from core.cache import CacheManager, ReferenceDataCache


class CustomExceptionHandlerTest(TestCase):
    """Тесты для custom_exception_handler"""
    
    def test_validation_error_handling(self):
        """Тест обработки ValidationError"""
        from django.core.exceptions import ValidationError
        
        exc = ValidationError("Ошибка валидации")
        context = {'request': None, 'view': None}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
    
    def test_other_exception_handling(self):
        """Тест обработки других исключений"""
        exc = Exception("Общая ошибка")
        context = {'request': None, 'view': None}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsNone(response)  # Возвращает None для необработанных исключений


class TelegramMessageTest(TestCase):
    """Тесты для отправки Telegram сообщений"""
    
    @patch('core.utils.requests.post')
    def test_send_telegram_message_success(self, mock_post):
        """Тест успешной отправки Telegram сообщения"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response
        
        result = send_telegram_message("Тестовое сообщение")
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('core.utils.requests.post')
    def test_send_telegram_message_failure(self, mock_post):
        """Тест неудачной отправки Telegram сообщения"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = send_telegram_message("Тестовое сообщение")
        
        self.assertFalse(result)
        mock_post.assert_called_once()
    
    @patch('core.utils.requests.post')
    def test_send_telegram_message_exception(self, mock_post):
        """Тест исключения при отправке Telegram сообщения"""
        mock_post.side_effect = Exception("Ошибка сети")
        
        result = send_telegram_message("Тестовое сообщение")
        
        self.assertFalse(result)


class TokenUtilsTest(TestCase):
    """Тесты для утилит работы с токенами"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        
        self.user = Polzovateli.objects.create(
            name='Тестовый Пользователь',
            login='testuser',
            password='testpass123',
            gorod=self.gorod,
            rol=self.rol,
            is_active=True
        )
        
        self.master = Master.objects.create(
            name='Тестовый мастер',
            login='testmaster',
            password=make_password('testpass123', hasher='pbkdf2_sha256'),
            gorod=self.gorod,
            phone='+79001234567',
            birth_date=date(1990, 1, 1),
            is_active=True
        )
    
    def test_get_user_from_token_valid(self):
        """Тест получения пользователя из валидного токена"""
        payload = {
            'user_id': self.user.id,
            'role': 'admin',
            'exp': (date.today() + timedelta(days=1)).isoformat()
        }
        token = jwt.encode(payload, 'devsecret', algorithm='HS256')
        
        user = get_user_from_token(token)
        
        self.assertEqual(user, self.user)
    
    def test_get_user_from_token_invalid(self):
        """Тест получения пользователя из невалидного токена"""
        token = "invalid_token"
        
        user = get_user_from_token(token)
        
        self.assertIsNone(user)
    
    def test_get_user_from_token_expired(self):
        """Тест получения пользователя из истёкшего токена"""
        payload = {
            'user_id': self.user.id,
            'role': 'admin',
            'exp': (date.today() - timedelta(days=1)).isoformat()
        }
        token = jwt.encode(payload, 'devsecret', algorithm='HS256')
        
        user = get_user_from_token(token)
        
        self.assertIsNone(user)
    
    def test_get_master_from_token_valid(self):
        """Тест получения мастера из валидного токена"""
        payload = {
            'master_id': self.master.id,
            'role': 'master',
            'exp': (date.today() + timedelta(days=1)).isoformat()
        }
        token = jwt.encode(payload, 'devsecret', algorithm='HS256')
        
        master = get_master_from_token(token)
        
        self.assertEqual(master, self.master)
    
    def test_get_master_from_token_invalid(self):
        """Тест получения мастера из невалидного токена"""
        token = "invalid_token"
        
        master = get_master_from_token(token)
        
        self.assertIsNone(master)


class DownloadAudioTest(TestCase):
    """Тесты для загрузки аудио файлов"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.master = Master.objects.create(
            name='Тестовый мастер',
            login='testmaster',
            password=make_password('testpass123', hasher='pbkdf2_sha256'),
            gorod=self.gorod
        )
        self.rk = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod,
            phone='+79001234567'
        )
        self.tip_zayavki = TipZayavki.objects.create(name='Ремонт холодильника')
        
        self.zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            master=self.master,
            rk=self.rk,
            tip_zayavki=self.tip_zayavki,
            phone_client='+79001234567',
            client_name='Клиент',
            status='Новая'
        )
    
    @patch('core.utils.os.path.exists')
    @patch('core.utils.shutil.copy2')
    def test_download_audio_success(self, mock_copy, mock_exists):
        """Тест успешной загрузки аудио файла"""
        mock_exists.return_value = True
        mock_copy.return_value = None
        
        result = download_audio_for_zayavka(self.zayavka.id, '+79001234567')
        
        self.assertTrue(result)
        mock_exists.assert_called()
        mock_copy.assert_called()
    
    @patch('core.utils.os.path.exists')
    def test_download_audio_file_not_found(self, mock_exists):
        """Тест загрузки аудио файла, когда файл не найден"""
        mock_exists.return_value = False
        
        result = download_audio_for_zayavka(self.zayavka.id, '+79001234567')
        
        self.assertFalse(result)
        mock_exists.assert_called()
    
    def test_download_audio_invalid_zayavka(self):
        """Тест загрузки аудио для несуществующей заявки"""
        result = download_audio_for_zayavka(99999, '+79001234567')
        
        self.assertFalse(result)


class CacheManagerTest(TestCase):
    """Тесты для CacheManager"""
    
    def setUp(self):
        cache.clear()
    
    def test_get_or_set_new_value(self):
        """Тест получения или установки нового значения"""
        def get_data():
            return {'test': 'data'}
        
        result = CacheManager.get_or_set('test_key', get_data)
        
        self.assertEqual(result, {'test': 'data'})
        
        # Проверяем, что значение кэшировано
        cached_result = CacheManager.get_or_set('test_key', lambda: {'different': 'data'})
        self.assertEqual(cached_result, {'test': 'data'})
    
    def test_get_or_set_existing_value(self):
        """Тест получения существующего значения из кэша"""
        # Сначала устанавливаем значение
        cache.set('test_key', {'existing': 'data'}, 300)
        
        def get_data():
            return {'new': 'data'}
        
        result = CacheManager.get_or_set('test_key', get_data)
        
        self.assertEqual(result, {'existing': 'data'})
    
    def test_invalidate_cache(self):
        """Тест инвалидации кэша"""
        # Устанавливаем значение
        cache.set('test_key', {'test': 'data'}, 300)
        
        # Инвалидируем
        CacheManager.invalidate_cache('test_key')
        
        # Проверяем, что значение удалено
        cached_value = cache.get('test_key')
        self.assertIsNone(cached_value)


class ReferenceDataCacheTest(TestCase):
    """Тесты для ReferenceDataCache"""
    
    def setUp(self):
        cache.clear()
        self.gorod = Gorod.objects.create(name='Москва')
        self.tip_zayavki = TipZayavki.objects.create(name='Ремонт холодильника')
        self.rk = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod,
            phone='+79001234567'
        )
    
    def test_get_goroda_cache_key(self):
        """Тест получения ключа кэша для городов"""
        key = ReferenceDataCache.get_goroda_cache_key()
        
        self.assertEqual(key, 'reference_data:goroda')
    
    def test_get_tipzayavki_cache_key(self):
        """Тест получения ключа кэша для типов заявок"""
        key = ReferenceDataCache.get_tipzayavki_cache_key()
        
        self.assertEqual(key, 'reference_data:tipzayavki')
    
    def test_get_rk_cache_key(self):
        """Тест получения ключа кэша для РК"""
        key = ReferenceDataCache.get_rk_cache_key()
        self.assertEqual(key, 'reference_data:rk')
        
        key_with_gorod = ReferenceDataCache.get_rk_cache_key(gorod_id=1)
        self.assertEqual(key_with_gorod, 'reference_data:rk:gorod:1')
    
    def test_invalidate_goroda_cache(self):
        """Тест инвалидации кэша городов"""
        # Устанавливаем значение в кэш
        cache.set('reference_data:goroda', [{'name': 'Москва'}], 300)
        
        # Инвалидируем
        ReferenceDataCache.invalidate_goroda_cache()
        
        # Проверяем, что значение удалено
        cached_value = cache.get('reference_data:goroda')
        self.assertIsNone(cached_value)
    
    def test_invalidate_tipzayavki_cache(self):
        """Тест инвалидации кэша типов заявок"""
        # Устанавливаем значение в кэш
        cache.set('reference_data:tipzayavki', [{'name': 'Ремонт'}], 300)
        
        # Инвалидируем
        ReferenceDataCache.invalidate_tipzayavki_cache()
        
        # Проверяем, что значение удалено
        cached_value = cache.get('reference_data:tipzayavki')
        self.assertIsNone(cached_value)
    
    def test_invalidate_rk_cache(self):
        """Тест инвалидации кэша РК"""
        # Устанавливаем значения в кэш
        cache.set('reference_data:rk', [{'name': 'РК'}], 300)
        cache.set('reference_data:rk:gorod:1', [{'name': 'РК Москва'}], 300)
        
        # Инвалидируем для конкретного города
        ReferenceDataCache.invalidate_rk_cache(gorod_id=1)
        
        # Проверяем, что значение удалено
        cached_value = cache.get('reference_data:rk:gorod:1')
        self.assertIsNone(cached_value)
        
        # Общий кэш тоже должен быть инвалидирован
        cached_value = cache.get('reference_data:rk')
        self.assertIsNone(cached_value)


class IntegrationUtilsTest(APITestCase):
    """Интеграционные тесты для utils"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Создаём базовые объекты
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        
        self.user = Polzovateli.objects.create(
            name='Тестовый Пользователь',
            login='testuser',
            password='testpass123',
            gorod=self.gorod,
            rol=self.rol,
            is_active=True
        )
    
    def test_custom_exception_handler_integration(self):
        """Интеграционный тест custom_exception_handler"""
        from django.core.exceptions import ValidationError
        from rest_framework.views import APIView
        from rest_framework.response import Response
        
        class TestView(APIView):
            def get(self, request):
                raise ValidationError("Тестовая ошибка валидации")
        
        view = TestView()
        request = self.client.get('/').wsgi_request
        
        # Симулируем исключение
        exc = ValidationError("Тестовая ошибка валидации")
        context = {'request': request, 'view': view}
        
        response = custom_exception_handler(exc, context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
    
    @patch('core.utils.send_telegram_message')
    def test_telegram_integration(self, mock_send):
        """Интеграционный тест отправки Telegram сообщений"""
        mock_send.return_value = True
        
        # Создаём заявку
        master = Master.objects.create(
            name='Тестовый мастер',
            login='testmaster',
            password=make_password('testpass123', hasher='pbkdf2_sha256'),
            gorod=self.gorod
        )
        rk = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod,
            phone='+79001234567'
        )
        tip_zayavki = TipZayavki.objects.create(name='Ремонт холодильника')
        
        zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            master=master,
            rk=rk,
            tip_zayavki=tip_zayavki,
            phone_client='+79001234567',
            client_name='Клиент',
            status='Новая'
        )
        
        # Отправляем уведомление
        result = send_telegram_message(f"Новая заявка #{zayavka.id}")
        
        self.assertTrue(result)
        mock_send.assert_called_once()
    
    def test_cache_integration(self):
        """Интеграционный тест кэширования"""
        # Создаём данные
        gorod1 = Gorod.objects.create(name='Москва')
        gorod2 = Gorod.objects.create(name='Санкт-Петербург')
        
        # Получаем данные через кэш
        def get_goroda_data():
            return list(Gorod.objects.values('id', 'name'))
        
        result1 = CacheManager.get_or_set('test_goroda', get_goroda_data)
        result2 = CacheManager.get_or_set('test_goroda', get_goroda_data)
        
        # Результаты должны быть одинаковыми
        self.assertEqual(result1, result2)
        self.assertEqual(len(result1), 2)
        
        # Инвалидируем кэш
        CacheManager.invalidate_cache('test_goroda')
        
        # Добавляем новый город
        gorod3 = Gorod.objects.create(name='Новосибирск')
        
        # Получаем обновленные данные
        result3 = CacheManager.get_or_set('test_goroda', get_goroda_data)
        
        # Должно быть 3 города
        self.assertEqual(len(result3), 3) 