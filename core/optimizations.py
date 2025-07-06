"""
Оптимизации для улучшения производительности базы данных
"""

from django.db import models
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Класс для оптимизации запросов к базе данных"""
    
    @staticmethod
    def optimize_zayavki_queryset():
        """Оптимизированный queryset для заявок"""
        from .models import Zayavki
        return Zayavki.objects.select_related(
            'gorod', 'master', 'rk', 'tip_zayavki'
        ).prefetch_related(
            'files'
        )
    
    @staticmethod
    def optimize_master_queryset():
        """Оптимизированный queryset для мастеров"""
        from .models import Master
        return Master.objects.select_related('gorod')
    
    @staticmethod
    def optimize_polzovateli_queryset():
        """Оптимизированный queryset для пользователей"""
        from .models import Polzovateli
        return Polzovateli.objects.select_related('gorod', 'rol')
    
    @staticmethod
    def optimize_tranzakcii_queryset():
        """Оптимизированный queryset для транзакций"""
        from .models import Tranzakcii
        return Tranzakcii.objects.select_related('gorod', 'tip_tranzakcii')
    
    @staticmethod
    def optimize_master_payout_queryset():
        """Оптимизированный queryset для выплат мастеров"""
        from .models import MasterPayout
        return MasterPayout.objects.select_related(
            'zayavka', 'zayavka__master', 'zayavka__gorod'
        )

class CacheOptimizer:
    """Класс для оптимизации кэширования"""
    
    CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 300)  # 5 минут по умолчанию
    
    @staticmethod
    def get_cache_key(prefix, **kwargs):
        """Генерация ключа кэша"""
        key_parts = [prefix]
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        return ":".join(key_parts)
    
    @staticmethod
    def cache_queryset_result(cache_key, queryset_func, timeout=None):
        """Кэширование результата queryset"""
        if timeout is None:
            timeout = CacheOptimizer.CACHE_TIMEOUT
        
        # Пытаемся получить из кэша
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_result
        
        # Выполняем запрос и кэшируем результат
        result = queryset_func()
        cache.set(cache_key, result, timeout)
        logger.debug(f"Cache miss for key: {cache_key}, cached for {timeout}s")
        return result
    
    @staticmethod
    def invalidate_cache_pattern(pattern):
        """Инвалидация кэша по паттерну"""
        # В Redis можно использовать SCAN для поиска ключей по паттерну
        # В простом случае просто логируем
        logger.info(f"Cache invalidation requested for pattern: {pattern}")

class DatabaseOptimizer:
    """Класс для оптимизации базы данных"""
    
    @staticmethod
    def get_optimized_queryset(model_class, select_related=None, prefetch_related=None):
        """Создание оптимизированного queryset"""
        queryset = model_class.objects.all()
        
        if select_related:
            queryset = queryset.select_related(*select_related)
        
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        return queryset
    
    @staticmethod
    def bulk_create_optimized(model_class, objects_data, batch_size=1000):
        """Оптимизированное массовое создание объектов"""
        objects = []
        for data in objects_data:
            objects.append(model_class(**data))
            
            if len(objects) >= batch_size:
                model_class.objects.bulk_create(objects)
                objects = []
        
        if objects:
            model_class.objects.bulk_create(objects)
    
    @staticmethod
    def bulk_update_optimized(queryset, fields, batch_size=1000):
        """Оптимизированное массовое обновление объектов"""
        queryset.bulk_update(queryset, fields, batch_size=batch_size)

class PerformanceMonitor:
    """Мониторинг производительности запросов"""
    
    @staticmethod
    def log_slow_query(query, execution_time, threshold=1.0):
        """Логирование медленных запросов"""
        if execution_time > threshold:
            logger.warning(
                f"Slow query detected: {execution_time:.2f}s > {threshold}s\n"
                f"Query: {query}"
            )
    
    @staticmethod
    def monitor_queryset_performance(queryset, operation_name):
        """Мониторинг производительности queryset"""
        import time
        start_time = time.time()
        
        try:
            result = list(queryset)
            execution_time = time.time() - start_time
            
            PerformanceMonitor.log_slow_query(
                f"{operation_name}: {len(result)} records",
                execution_time
            )
            
            return result
        except Exception as e:
            logger.error(f"Error in {operation_name}: {e}")
            raise 