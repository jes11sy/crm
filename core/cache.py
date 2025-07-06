from django.core.cache import cache
from django.conf import settings
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Менеджер кэширования для справочных данных CRM системы.
    """
    
    # Время жизни кэша для разных типов данных (в секундах)
    CACHE_TIMEOUTS = {
        'reference_data': 3600,  # 1 час для справочников
        'user_data': 1800,       # 30 минут для данных пользователей
        'query_results': 300,    # 5 минут для результатов запросов
        'session_data': 86400,   # 24 часа для сессий
    }
    
    @classmethod
    def get_cache_key(cls, prefix: str, identifier: str) -> str:
        """Генерирует ключ кэша с префиксом."""
        return f"{prefix}:{identifier}"
    
    @classmethod
    def set_data(cls, key: str, data: Any, timeout: Optional[int] = None, cache_type: str = 'reference_data') -> bool:
        """
        Сохраняет данные в кэш.
        
        Args:
            key: Ключ кэша
            data: Данные для сохранения
            timeout: Время жизни в секундах (если None, используется по умолчанию)
            cache_type: Тип кэша для определения времени жизни по умолчанию
            
        Returns:
            bool: True если данные сохранены успешно
        """
        try:
            if timeout is None:
                timeout = cls.CACHE_TIMEOUTS.get(cache_type, 300)
            
            cache_key = cls.get_cache_key('crm', key)
            cache.set(cache_key, data, timeout)
            
            logger.debug(f"Data cached successfully: {key}, timeout: {timeout}s")
            return True
            
        except Exception as e:
            logger.error(f"Error caching data {key}: {e}")
            return False
    
    @classmethod
    def get_data(cls, key: str) -> Any:
        """
        Получает данные из кэша.
        
        Args:
            key: Ключ кэша
            
        Returns:
            Any: Данные из кэша или None если не найдены
        """
        try:
            cache_key = cls.get_cache_key('crm', key)
            data = cache.get(cache_key)
            
            if data is not None:
                logger.debug(f"Cache hit: {key}")
            else:
                logger.debug(f"Cache miss: {key}")
                
            return data
            
        except Exception as e:
            logger.error(f"Error getting cached data {key}: {e}")
            return None
    
    @classmethod
    def delete_data(cls, key: str) -> bool:
        """
        Удаляет данные из кэша.
        
        Args:
            key: Ключ кэша
            
        Returns:
            bool: True если данные удалены успешно
        """
        try:
            cache_key = cls.get_cache_key('crm', key)
            cache.delete(cache_key)
            
            logger.debug(f"Data deleted from cache: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cached data {key}: {e}")
            return False
    
    @classmethod
    def clear_pattern(cls, pattern: str) -> bool:
        """
        Очищает все ключи, соответствующие паттерну.
        
        Args:
            pattern: Паттерн для поиска ключей
            
        Returns:
            bool: True если очистка прошла успешно
        """
        try:
            # Получаем все ключи, соответствующие паттерну
            keys = cache.keys(f"crm:{pattern}*")
            
            if keys:
                cache.delete_many(keys)
                logger.info(f"Cleared {len(keys)} cache keys matching pattern: {pattern}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return False
    
    @classmethod
    def get_or_set(cls, key: str, getter_func, timeout: Optional[int] = None, cache_type: str = 'reference_data') -> Any:
        """
        Получает данные из кэша или создает их с помощью функции.
        
        Args:
            key: Ключ кэша
            getter_func: Функция для получения данных если их нет в кэше
            timeout: Время жизни в секундах
            cache_type: Тип кэша
            
        Returns:
            Any: Данные из кэша или полученные функцией
        """
        # Пытаемся получить из кэша
        cached_data = cls.get_data(key)
        
        if cached_data is not None:
            return cached_data
        
        # Если данных нет в кэше, получаем их функцией
        try:
            data = getter_func()
            
            if data is not None:
                cls.set_data(key, data, timeout, cache_type)
            
            return data
            
        except Exception as e:
            logger.error(f"Error in get_or_set for key {key}: {e}")
            return None

# Специализированные функции для справочных данных
class ReferenceDataCache:
    """Кэширование справочных данных."""
    
    @staticmethod
    def get_goroda_cache_key() -> str:
        return "reference:goroda:all"
    
    @staticmethod
    def get_tipzayavki_cache_key() -> str:
        return "reference:tipzayavki:all"
    
    @staticmethod
    def get_rk_cache_key(gorod_id: Optional[int] = None) -> str:
        if gorod_id:
            return f"reference:rk:gorod:{gorod_id}"
        return "reference:rk:all"
    
    @staticmethod
    def get_master_cache_key(gorod_id: Optional[int] = None, active_only: bool = False) -> str:
        if gorod_id:
            return f"reference:master:gorod:{gorod_id}:active:{active_only}"
        return f"reference:master:all:active:{active_only}"
    
    @staticmethod
    def get_tiptranzakcii_cache_key() -> str:
        return "reference:tiptranzakcii:all"
    
    @staticmethod
    def get_phonegoroda_cache_key(gorod_id: Optional[int] = None) -> str:
        if gorod_id:
            return f"reference:phonegoroda:gorod:{gorod_id}"
        return "reference:phonegoroda:all"
    
    @staticmethod
    def invalidate_goroda_cache():
        """Инвалидирует кэш городов."""
        CacheManager.clear_pattern("reference:goroda")
    
    @staticmethod
    def invalidate_tipzayavki_cache():
        """Инвалидирует кэш типов заявок."""
        CacheManager.clear_pattern("reference:tipzayavki")
    
    @staticmethod
    def invalidate_rk_cache(gorod_id: Optional[int] = None):
        """Инвалидирует кэш РК."""
        if gorod_id:
            CacheManager.clear_pattern(f"reference:rk:gorod:{gorod_id}")
        else:
            CacheManager.clear_pattern("reference:rk")
    
    @staticmethod
    def invalidate_master_cache(gorod_id: Optional[int] = None):
        """Инвалидирует кэш мастеров."""
        if gorod_id:
            CacheManager.clear_pattern(f"reference:master:gorod:{gorod_id}")
        else:
            CacheManager.clear_pattern("reference:master")
    
    @staticmethod
    def invalidate_tiptranzakcii_cache():
        """Инвалидирует кэш типов транзакций."""
        CacheManager.clear_pattern("reference:tiptranzakcii")
    
    @staticmethod
    def invalidate_phonegoroda_cache(gorod_id: Optional[int] = None):
        """Инвалидирует кэш телефонов городов."""
        if gorod_id:
            CacheManager.clear_pattern(f"reference:phonegoroda:gorod:{gorod_id}")
        else:
            CacheManager.clear_pattern("reference:phonegoroda")

# Функции для кэширования пользовательских данных
class UserDataCache:
    """Кэширование данных пользователей."""
    
    @staticmethod
    def get_user_cache_key(user_id: int) -> str:
        return f"user:{user_id}:data"
    
    @staticmethod
    def get_user_permissions_cache_key(user_id: int) -> str:
        return f"user:{user_id}:permissions"
    
    @staticmethod
    def cache_user_data(user_id: int, user_data: Dict[str, Any]) -> bool:
        """Кэширует данные пользователя."""
        key = UserDataCache.get_user_cache_key(user_id)
        return CacheManager.set_data(key, user_data, cache_type='user_data')
    
    @staticmethod
    def get_cached_user_data(user_id: int) -> Optional[Dict[str, Any]]:
        """Получает кэшированные данные пользователя."""
        key = UserDataCache.get_user_cache_key(user_id)
        return CacheManager.get_data(key)
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Инвалидирует кэш пользователя."""
        CacheManager.clear_pattern(f"user:{user_id}")

# Декоратор для кэширования методов
def cache_method_result(timeout: Optional[int] = None, cache_type: str = 'reference_data'):
    """
    Декоратор для кэширования результатов методов.
    
    Args:
        timeout: Время жизни кэша в секундах
        cache_type: Тип кэша
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Создаем ключ кэша на основе имени функции и аргументов
            cache_key = f"method:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            return CacheManager.get_or_set(
                cache_key, 
                lambda: func(*args, **kwargs), 
                timeout, 
                cache_type
            )
        return wrapper
    return decorator 