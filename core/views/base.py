from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import transaction
from ..models import Gorod, TipZayavki, RK, PhoneGoroda
from ..serializers import GorodSerializer, TipZayavkiSerializer, RKSerializer, PhoneGorodaSerializer
from ..permissions import IsCallCentreOrAbove, IsDirectorOrAdmin
from ..cache import ReferenceDataCache, CacheManager
import logging

logger = logging.getLogger(__name__)

class BaseViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet с общей функциональностью"""
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error in {self.__class__.__name__}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating {self.__class__.__name__}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().update(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error in {self.__class__.__name__}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating {self.__class__.__name__}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error deleting {self.__class__.__name__}: {e}")
            return Response({'error': 'Ошибка при удалении'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema_view(
    list=extend_schema(
        summary="Получить список городов",
        description="Возвращает список всех городов с кэшированием",
        tags=['gorod']
    ),
    create=extend_schema(
        summary="Создать город",
        description="Создаёт новый город и инвалидирует кэш",
        tags=['gorod']
    ),
    update=extend_schema(
        summary="Обновить город",
        description="Обновляет существующий город и инвалидирует кэш",
        tags=['gorod']
    ),
    destroy=extend_schema(
        summary="Удалить город",
        description="Удаляет город и инвалидирует кэш",
        tags=['gorod']
    )
)
class GorodViewSet(BaseViewSet):
    queryset = Gorod.objects.all()
    serializer_class = GorodSerializer
    permission_classes = [IsCallCentreOrAbove]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']
    def list(self, request, *args, **kwargs):
        cache_key = ReferenceDataCache.get_goroda_cache_key()
        def get_goroda_data():
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return serializer.data
        data = CacheManager.get_or_set(cache_key, get_goroda_data)
        return Response(data)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        ReferenceDataCache.invalidate_goroda_cache()
        return response
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        ReferenceDataCache.invalidate_goroda_cache()
        return response
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        ReferenceDataCache.invalidate_goroda_cache()
        return response

class TipZayavkiViewSet(BaseViewSet):
    queryset = TipZayavki.objects.all()
    serializer_class = TipZayavkiSerializer
    permission_classes = [IsCallCentreOrAbove]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']
    def list(self, request, *args, **kwargs):
        cache_key = ReferenceDataCache.get_tipzayavki_cache_key()
        def get_tipzayavki_data():
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return serializer.data
        data = CacheManager.get_or_set(cache_key, get_tipzayavki_data)
        return Response(data)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        ReferenceDataCache.invalidate_tipzayavki_cache()
        return response
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        ReferenceDataCache.invalidate_tipzayavki_cache()
        return response
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        ReferenceDataCache.invalidate_tipzayavki_cache()
        return response

class RKViewSet(BaseViewSet):
    queryset = RK.objects.all()
    serializer_class = RKSerializer
    permission_classes = [IsCallCentreOrAbove]
    filterset_fields = ['rk_name', 'gorod', 'phone']
    search_fields = ['rk_name', 'phone']
    ordering_fields = ['rk_name', 'gorod']
    def list(self, request, *args, **kwargs):
        gorod_filter = request.query_params.get('gorod')
        cache_key = ReferenceDataCache.get_rk_cache_key(gorod_filter)
        def get_rk_data():
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return serializer.data
        data = CacheManager.get_or_set(cache_key, get_rk_data)
        return Response(data)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        gorod_id = request.data.get('gorod')
        ReferenceDataCache.invalidate_rk_cache(gorod_id)
        return response
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        instance = self.get_object()
        ReferenceDataCache.invalidate_rk_cache(instance.gorod.id)
        return response
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        gorod_id = instance.gorod.id
        response = super().destroy(request, *args, **kwargs)
        ReferenceDataCache.invalidate_rk_cache(gorod_id)
        return response

class PhoneGorodaViewSet(BaseViewSet):
    queryset = PhoneGoroda.objects.all()
    serializer_class = PhoneGorodaSerializer
    permission_classes = [IsDirectorOrAdmin]
    filterset_fields = ['gorod', 'phone']
    search_fields = ['phone']
    ordering_fields = ['gorod', 'phone'] 