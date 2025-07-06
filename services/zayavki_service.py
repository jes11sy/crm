"""
Сервис для работы с заявками.
В будущем может быть выделен в отдельный микросервис.
"""

import logging
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Zayavki, ZayavkaFile, Master, Gorod
from core.serializers import ZayavkiSerializer, ZayavkaFileSerializer

logger = logging.getLogger(__name__)

class ZayavkiService:
    """Сервис для работы с заявками"""
    
    @staticmethod
    def get_zayavki_for_master(master_id, filters=None):
        """Получение заявок для мастера"""
        try:
            queryset = Zayavki.objects.filter(master_id=master_id)
            
            if filters:
                if filters.get('status'):
                    queryset = queryset.filter(status=filters['status'])
                if filters.get('date_from'):
                    queryset = queryset.filter(data_zayavki__gte=filters['date_from'])
                if filters.get('date_to'):
                    queryset = queryset.filter(data_zayavki__lte=filters['date_to'])
                if filters.get('tip_zayavki'):
                    queryset = queryset.filter(tip_zayavki=filters['tip_zayavki'])
            
            return queryset.order_by('-data_zayavki')
            
        except Exception as e:
            logger.error(f"Ошибка получения заявок для мастера {master_id}: {e}")
            return Zayavki.objects.none()
    
    @staticmethod
    def get_zayavki_statistics(master_id=None, date_from=None, date_to=None):
        """Получение статистики по заявкам"""
        try:
            queryset = Zayavki.objects.all()
            
            if master_id:
                queryset = queryset.filter(master_id=master_id)
            
            if date_from:
                queryset = queryset.filter(data_zayavki__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(data_zayavki__lte=date_to)
            
            stats = queryset.aggregate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                in_progress=Count('id', filter=Q(status='in_progress')),
                pending=Count('id', filter=Q(status='pending')),
                cancelled=Count('id', filter=Q(status='cancelled'))
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики заявок: {e}")
            return {}
    
    @staticmethod
    def create_zayavka(data):
        """Создание новой заявки"""
        try:
            serializer = ZayavkiSerializer(data=data)
            if serializer.is_valid():
                zayavka = serializer.save()
                logger.info(f"Создана заявка {zayavka.id}")
                return zayavka, None
            else:
                return None, serializer.errors
                
        except Exception as e:
            logger.error(f"Ошибка создания заявки: {e}")
            return None, {'error': str(e)}
    
    @staticmethod
    def update_zayavka(zayavka_id, data):
        """Обновление заявки"""
        try:
            zayavka = Zayavki.objects.get(id=zayavka_id)
            serializer = ZayavkiSerializer(zayavka, data=data, partial=True)
            
            if serializer.is_valid():
                updated_zayavka = serializer.save()
                logger.info(f"Обновлена заявка {zayavka_id}")
                return updated_zayavka, None
            else:
                return None, serializer.errors
                
        except Zayavki.DoesNotExist:
            return None, {'error': 'Заявка не найдена'}
        except Exception as e:
            logger.error(f"Ошибка обновления заявки {zayavka_id}: {e}")
            return None, {'error': str(e)}
    
    @staticmethod
    def add_file_to_zayavka(zayavka_id, file_data):
        """Добавление файла к заявке"""
        try:
            file_data['zayavka_id'] = zayavka_id
            serializer = ZayavkaFileSerializer(data=file_data)
            
            if serializer.is_valid():
                file_obj = serializer.save()
                logger.info(f"Добавлен файл {file_obj.id} к заявке {zayavka_id}")
                return file_obj, None
            else:
                return None, serializer.errors
                
        except Exception as e:
            logger.error(f"Ошибка добавления файла к заявке {zayavka_id}: {e}")
            return None, {'error': str(e)}

class ZayavkiAnalyticsService:
    """Сервис аналитики заявок"""
    
    @staticmethod
    def get_master_performance(master_id, period_days=30):
        """Получение производительности мастера"""
        try:
            date_from = timezone.now() - timedelta(days=period_days)
            
            stats = Zayavki.objects.filter(
                master_id=master_id,
                data_zayavki__gte=date_from
            ).aggregate(
                total_zayavki=Count('id'),
                completed_zayavki=Count('id', filter=Q(status='completed')),
                avg_completion_time=Sum('completion_time') / Count('id', filter=Q(status='completed'))
            )
            
            if stats['total_zayavki'] > 0:
                completion_rate = (stats['completed_zayavki'] / stats['total_zayavki']) * 100
            else:
                completion_rate = 0
            
            return {
                'total_zayavki': stats['total_zayavki'],
                'completed_zayavki': stats['completed_zayavki'],
                'completion_rate': round(completion_rate, 2),
                'avg_completion_time': stats['avg_completion_time'] or 0
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения производительности мастера {master_id}: {e}")
            return {}
    
    @staticmethod
    def get_city_statistics(city_id=None, period_days=30):
        """Получение статистики по городам"""
        try:
            date_from = timezone.now() - timedelta(days=period_days)
            
            queryset = Zayavki.objects.filter(data_zayavki__gte=date_from)
            
            if city_id:
                queryset = queryset.filter(gorod_id=city_id)
            
            stats = queryset.values('gorod__name').annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                in_progress=Count('id', filter=Q(status='in_progress'))
            ).order_by('-total')
            
            return list(stats)
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики по городам: {e}")
            return [] 