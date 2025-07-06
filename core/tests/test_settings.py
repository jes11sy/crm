"""
Настройки для тестов
"""
from django.test import TestCase
from django.conf import settings

# Настройки для тестов
TEST_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    },
    'TELEGRAM_BOT_TOKEN': 'test_token',
    'TELEGRAM_CHAT_ID': 123456789,
    'MANGO_API_KEY': 'test_mango_key',
    'MANGO_API_SALT': 'test_mango_salt',
    'SECRET_KEY': 'test_secret_key',
    'DEBUG': True,
    'ALERTS_ENABLED': False,
    'ALERT_EMAIL_ENABLED': False,
}


class TestSettingsMixin:
    """Миксин для настройки тестового окружения"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Применяем тестовые настройки
        for key, value in TEST_SETTINGS.items():
            setattr(settings, key, value)
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Восстанавливаем оригинальные настройки
        for key in TEST_SETTINGS:
            if hasattr(settings, f'ORIGINAL_{key}'):
                setattr(settings, key, getattr(settings, f'ORIGINAL_{key}'))


class BaseTestCase(TestCase, TestSettingsMixin):
    """Базовый класс для всех тестов"""
    
    def setUp(self):
        super().setUp()
        # Очищаем кэш перед каждым тестом
        from django.core.cache import cache
        cache.clear()
    
    def tearDown(self):
        super().tearDown()
        # Очищаем кэш после каждого теста
        from django.core.cache import cache
        cache.clear() 