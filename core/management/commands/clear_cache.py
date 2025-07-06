from django.core.management.base import BaseCommand
from django.core.cache import cache
from core.cache import CacheManager, ReferenceDataCache
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Очищает кэш Redis для CRM системы'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Очистить весь кэш',
        )
        parser.add_argument(
            '--reference',
            action='store_true',
            help='Очистить только справочные данные',
        )
        parser.add_argument(
            '--users',
            action='store_true',
            help='Очистить кэш пользователей',
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Очистить кэш по паттерну (например: "reference:goroda")',
        )
    
    def handle(self, *args, **options):
        if options['all']:
            self.clear_all_cache()
        elif options['reference']:
            self.clear_reference_cache()
        elif options['users']:
            self.clear_users_cache()
        elif options['pattern']:
            self.clear_pattern_cache(options['pattern'])
        else:
            self.stdout.write(
                self.style.WARNING('Укажите тип кэша для очистки. Используйте --help для справки.')
            )
    
    def clear_all_cache(self):
        """Очищает весь кэш."""
        try:
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Весь кэш успешно очищен')
            )
            logger.info('All cache cleared via management command')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при очистке кэша: {e}')
            )
            logger.error(f'Error clearing all cache: {e}')
    
    def clear_reference_cache(self):
        """Очищает кэш справочных данных."""
        try:
            # Очищаем все справочные данные
            patterns = [
                'reference:goroda',
                'reference:tipzayavki', 
                'reference:rk',
                'reference:master',
                'reference:tiptranzakcii',
                'reference:phonegoroda'
            ]
            
            cleared_count = 0
            for pattern in patterns:
                if CacheManager.clear_pattern(pattern):
                    cleared_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш справочных данных очищен. Обработано паттернов: {cleared_count}')
            )
            logger.info(f'Reference cache cleared. Patterns processed: {cleared_count}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при очистке справочного кэша: {e}')
            )
            logger.error(f'Error clearing reference cache: {e}')
    
    def clear_users_cache(self):
        """Очищает кэш пользователей."""
        try:
            if CacheManager.clear_pattern('user:'):
                self.stdout.write(
                    self.style.SUCCESS('Кэш пользователей успешно очищен')
                )
                logger.info('Users cache cleared via management command')
            else:
                self.stdout.write(
                    self.style.WARNING('Кэш пользователей не найден или уже пуст')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при очистке кэша пользователей: {e}')
            )
            logger.error(f'Error clearing users cache: {e}')
    
    def clear_pattern_cache(self, pattern):
        """Очищает кэш по указанному паттерну."""
        try:
            if CacheManager.clear_pattern(pattern):
                self.stdout.write(
                    self.style.SUCCESS(f'Кэш по паттерну "{pattern}" успешно очищен')
                )
                logger.info(f'Cache cleared for pattern: {pattern}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'Кэш по паттерну "{pattern}" не найден')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при очистке кэша по паттерну "{pattern}": {e}')
            )
            logger.error(f'Error clearing cache for pattern {pattern}: {e}') 