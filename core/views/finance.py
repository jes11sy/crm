from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from ..models import TipTranzakcii, Tranzakcii, MasterPayout
from ..serializers import TipTranzakciiSerializer, TranzakciiSerializer, MasterPayoutSerializer
from ..permissions import IsDirectorOrAdmin, IsSameCity, IsMasterOrAbove
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TipTranzakciiViewSet(viewsets.ModelViewSet):
    queryset = TipTranzakcii.objects.all()
    serializer_class = TipTranzakciiSerializer
    permission_classes = [IsDirectorOrAdmin]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']

class TranzakciiViewSet(viewsets.ModelViewSet):
    queryset = Tranzakcii.objects.select_related('gorod', 'tip_tranzakcii')
    serializer_class = TranzakciiSerializer
    permission_classes = [IsSameCity]
    filterset_fields = ['gorod', 'tip_tranzakcii', 'date']
    search_fields = ['note']
    ordering_fields = ['date', 'created_at', 'summa']
    
    def get_queryset(self):
        """Оптимизированный queryset с фильтрацией по городу пользователя"""
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'gorod_id'):
            return queryset.filter(gorod_id=user.gorod_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Получение транзакций по диапазону дат с группировкой"""
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date or not end_date:
                return Response({'error': 'Необходимо указать start_date и end_date'}, status=400)
            
            # Парсим даты
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Фильтруем по диапазону дат с оптимизацией
            queryset = self.get_queryset().filter(date__range=[start, end])
            
            # Группируем по типу транзакции
            result = {}
            for tranzakciya in queryset:
                tip_name = tranzakciya.tip_tranzakcii.name
                if tip_name not in result:
                    result[tip_name] = {
                        'count': 0,
                        'total': 0
                    }
                result[tip_name]['count'] += 1
                result[tip_name]['total'] += float(tranzakciya.summa)
            
            return Response(result)
            
        except ValueError as e:
            return Response({'error': 'Неверный формат даты'}, status=400)
        except Exception as e:
            logger.error(f"Error in by_date_range: {e}")
            return Response({'error': 'Ошибка при обработке запроса'}, status=500)

class MasterPayoutViewSet(viewsets.ModelViewSet):
    queryset = MasterPayout.objects.select_related('zayavka', 'zayavka__master', 'zayavka__gorod')
    serializer_class = MasterPayoutSerializer
    permission_classes = [IsMasterOrAbove]
    filterset_fields = ['status', 'zayavka', 'zayavka__master']
    search_fields = ['comment']
    ordering_fields = ['created_at', 'summa', 'status']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Оптимизированный queryset с фильтрацией по городу пользователя"""
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'gorod_id'):
            return queryset.filter(zayavka__gorod_id=user.gorod_id)
        return queryset 