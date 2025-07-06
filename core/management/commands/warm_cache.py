from django.core.management.base import BaseCommand
from django.core.cache import cache
from core.cache import CacheManager, ReferenceDataCache
from core.models import Gorod, TipZayavki, RK, Master, TipTranzakcii, PhoneGoroda
from core.serializers import (
    GorodSerializer, TipZayavkiSerializer, RKSerializer, 
    MasterSerializer, TipTranzakciiSerializer, PhoneGorodaSerializer
)
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Предварительно заполняет кэш Redis справочными данными'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Заполнить весь кэш справочных данных',
        )
        parser.add_argument(
            '--goroda',
            action='store_true',
            help='Заполнить кэш городов',
        )
        parser.add_argument(
            '--tipzayavki',
            action='store_true',
            help='Заполнить кэш типов заявок',
        )
        parser.add_argument(
            '--rk',
            action='store_true',
            help='Заполнить кэш РК',
        )
        parser.add_argument(
            '--master',
            action='store_true',
            help='Заполнить кэш мастеров',
        )
        parser.add_argument(
            '--tiptranzakcii',
            action='store_true',
            help='Заполнить кэш типов транзакций',
        )
        parser.add_argument(
            '--phonegoroda',
            action='store_true',
            help='Заполнить кэш телефонов городов',
        )
    
    def handle(self, *args, **options):
        if options['all']:
            self.warm_all_cache()
        elif options['goroda']:
            self.warm_goroda_cache()
        elif options['tipzayavki']:
            self.warm_tipzayavki_cache()
        elif options['rk']:
            self.warm_rk_cache()
        elif options['master']:
            self.warm_master_cache()
        elif options['tiptranzakcii']:
            self.warm_tiptranzakcii_cache()
        elif options['phonegoroda']:
            self.warm_phonegoroda_cache()
        else:
            self.stdout.write(
                self.style.WARNING('Укажите тип данных для заполнения кэша. Используйте --help для справки.')
            )
    
    def warm_all_cache(self):
        """Заполняет весь кэш справочных данных."""
        self.stdout.write('Начинаем заполнение всего кэша справочных данных...')
        
        self.warm_goroda_cache()
        self.warm_tipzayavki_cache()
        self.warm_rk_cache()
        self.warm_master_cache()
        self.warm_tiptranzakcii_cache()
        self.warm_phonegoroda_cache()
        
        self.stdout.write(
            self.style.SUCCESS('Весь кэш справочных данных успешно заполнен')
        )
    
    def warm_goroda_cache(self):
        """Заполняет кэш городов."""
        try:
            cache_key = ReferenceDataCache.get_goroda_cache_key()
            queryset = Gorod.objects.all()
            serializer = GorodSerializer(queryset, many=True)
            
            CacheManager.set_data(cache_key, serializer.data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш городов заполнен: {queryset.count()} записей')
            )
            logger.info(f'Goroda cache warmed: {queryset.count()} records')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при заполнении кэша городов: {e}')
            )
            logger.error(f'Error warming goroda cache: {e}')
    
    def warm_tipzayavki_cache(self):
        """Заполняет кэш типов заявок."""
        try:
            cache_key = ReferenceDataCache.get_tipzayavki_cache_key()
            queryset = TipZayavki.objects.all()
            serializer = TipZayavkiSerializer(queryset, many=True)
            
            CacheManager.set_data(cache_key, serializer.data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш типов заявок заполнен: {queryset.count()} записей')
            )
            logger.info(f'TipZayavki cache warmed: {queryset.count()} records')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при заполнении кэша типов заявок: {e}')
            )
            logger.error(f'Error warming tipzayavki cache: {e}')
    
    def warm_rk_cache(self):
        """Заполняет кэш РК."""
        try:
            # Общий кэш для всех РК
            cache_key = ReferenceDataCache.get_rk_cache_key()
            queryset = RK.objects.all()
            serializer = RKSerializer(queryset, many=True)
            
            CacheManager.set_data(cache_key, serializer.data)
            
            # Кэш для каждого города отдельно
            cities = Gorod.objects.all()
            for city in cities:
                city_rk = RK.objects.filter(gorod=city)
                city_serializer = RKSerializer(city_rk, many=True)
                city_cache_key = ReferenceDataCache.get_rk_cache_key(city.id)
                CacheManager.set_data(city_cache_key, city_serializer.data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш РК заполнен: {queryset.count()} записей, {cities.count()} городов')
            )
            logger.info(f'RK cache warmed: {queryset.count()} records, {cities.count()} cities')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при заполнении кэша РК: {e}')
            )
            logger.error(f'Error warming RK cache: {e}')
    
    def warm_master_cache(self):
        """Заполняет кэш мастеров."""
        try:
            # Общий кэш для всех мастеров
            all_masters = Master.objects.all()
            all_serializer = MasterSerializer(all_masters, many=True)
            all_cache_key = ReferenceDataCache.get_master_cache_key()
            CacheManager.set_data(all_cache_key, all_serializer.data)
            
            # Кэш для активных мастеров
            active_masters = Master.objects.filter(is_active=True)
            active_serializer = MasterSerializer(active_masters, many=True)
            active_cache_key = ReferenceDataCache.get_master_cache_key(active_only=True)
            CacheManager.set_data(active_cache_key, active_serializer.data)
            
            # Кэш для каждого города
            cities = Gorod.objects.all()
            for city in cities:
                city_masters = Master.objects.filter(gorod=city)
                city_serializer = MasterSerializer(city_masters, many=True)
                city_cache_key = ReferenceDataCache.get_master_cache_key(city.id)
                CacheManager.set_data(city_cache_key, city_serializer.data)
                
                # Активные мастера для города
                city_active_masters = Master.objects.filter(gorod=city, is_active=True)
                city_active_serializer = MasterSerializer(city_active_masters, many=True)
                city_active_cache_key = ReferenceDataCache.get_master_cache_key(city.id, active_only=True)
                CacheManager.set_data(city_active_cache_key, city_active_serializer.data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш мастеров заполнен: {all_masters.count()} записей, {cities.count()} городов')
            )
            logger.info(f'Master cache warmed: {all_masters.count()} records, {cities.count()} cities')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при заполнении кэша мастеров: {e}')
            )
            logger.error(f'Error warming master cache: {e}')
    
    def warm_tiptranzakcii_cache(self):
        """Заполняет кэш типов транзакций."""
        try:
            cache_key = ReferenceDataCache.get_tiptranzakcii_cache_key()
            queryset = TipTranzakcii.objects.all()
            serializer = TipTranzakciiSerializer(queryset, many=True)
            
            CacheManager.set_data(cache_key, serializer.data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш типов транзакций заполнен: {queryset.count()} записей')
            )
            logger.info(f'TipTranzakcii cache warmed: {queryset.count()} records')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при заполнении кэша типов транзакций: {e}')
            )
            logger.error(f'Error warming tiptranzakcii cache: {e}')
    
    def warm_phonegoroda_cache(self):
        """Заполняет кэш телефонов городов."""
        try:
            # Общий кэш для всех телефонов
            cache_key = ReferenceDataCache.get_phonegoroda_cache_key()
            queryset = PhoneGoroda.objects.all()
            serializer = PhoneGorodaSerializer(queryset, many=True)
            
            CacheManager.set_data(cache_key, serializer.data)
            
            # Кэш для каждого города отдельно
            cities = Gorod.objects.all()
            for city in cities:
                city_phones = PhoneGoroda.objects.filter(gorod=city)
                city_serializer = PhoneGorodaSerializer(city_phones, many=True)
                city_cache_key = ReferenceDataCache.get_phonegoroda_cache_key(city.id)
                CacheManager.set_data(city_cache_key, city_serializer.data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш телефонов городов заполнен: {queryset.count()} записей, {cities.count()} городов')
            )
            logger.info(f'PhoneGoroda cache warmed: {queryset.count()} records, {cities.count()} cities')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при заполнении кэша телефонов городов: {e}')
            )
            logger.error(f'Error warming phonegoroda cache: {e}') 