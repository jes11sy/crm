from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from ..models import Zayavki, ZayavkaFile
from ..serializers import ZayavkiSerializer, ZayavkaFileSerializer
from ..permissions import IsKCUserOrAbove, IsSameCity
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from pathlib import Path
import os
import traceback
import logging
import json
import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = '8032155601:AAG9myXmM3tO12LRFsX9T64wVIEdi6pexi8'
TELEGRAM_CHAT_ID = 1802367546

class ZayavkiViewSet(viewsets.ModelViewSet):
    queryset = Zayavki.objects.select_related('gorod', 'master', 'rk', 'tip_zayavki').prefetch_related('files')
    serializer_class = ZayavkiSerializer
    permission_classes = [IsKCUserOrAbove, IsSameCity]
    filterset_fields = ['status', 'gorod', 'master', 'rk', 'tip_zayavki']
    search_fields = ['client_name', 'phone_client', 'address']
    ordering_fields = ['created_at', 'meeting_date', 'status']
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'gorod_id'):
            return queryset.filter(gorod_id=user.gorod_id)
        return queryset
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        status_param = request.query_params.get('status')
        queryset = self.get_queryset().filter(status=status_param)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def incoming(self, request):
        queryset = self.get_queryset().filter(status='Ожидает')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ZayavkaFileViewSet(viewsets.ModelViewSet):
    queryset = ZayavkaFile.objects.all()
    serializer_class = ZayavkaFileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return super().get_queryset()
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

def mango_audio_files(request):
    try:
        # Получаем параметры из запроса
        file_path = request.GET.get('file_path')
        if not file_path:
            return JsonResponse({'error': 'Не указан путь к файлу'}, status=400)
        
        # Проверяем существование файла
        full_path = Path(file_path)
        if not full_path.exists():
            return JsonResponse({'error': 'Файл не найден'}, status=404)
        
        # Отправляем файл
        with open(full_path, 'rb') as f:
            response = JsonResponse(f.read())
            response['Content-Type'] = 'audio/mpeg'
            response['Content-Disposition'] = f'attachment; filename="{full_path.name}"'
            return response
            
    except Exception as e:
        logger.error(f"Error serving mango audio file: {e}")
        return JsonResponse({'error': 'Ошибка при обработке файла'}, status=500)

class MangoIncomingCallView(APIView):
    permission_classes = []
    def normalize_phone(self, phone):
        # Убираем все символы кроме цифр
        phone = ''.join(filter(str.isdigit, str(phone)))
        # Добавляем 7 если номер начинается с 8 или 9
        if phone.startswith('8'):
            phone = '7' + phone[1:]
        elif phone.startswith('9') and len(phone) == 10:
            phone = '7' + phone
        return phone
    def post(self, request):
        try:
            # Получаем данные от Mango
            data = request.data
            logger.info(f"Mango incoming call data: {data}")
            
            # Извлекаем номер телефона
            phone = data.get('from', {}).get('number', '')
            if not phone:
                return Response({'error': 'Не указан номер телефона'}, status=400)
            
            # Нормализуем номер
            normalized_phone = self.normalize_phone(phone)
            
            # Создаем заявку
            zayavka = Zayavki.objects.create(
                phone_client=normalized_phone,
                client_name='Звонок с Mango',
                address='Не указан',
                meeting_date=timezone.now(),
                tip_techniki='Не указано',
                problema='Входящий звонок',
                status='Ожидает',
                kc_name='Mango'
            )
            
            # Отправляем уведомление в Telegram
            message = f"📞 Новый входящий звонок\nНомер: {normalized_phone}\nЗаявка: {zayavka.id}"
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    data={
                        'chat_id': TELEGRAM_CHAT_ID,
                        'text': message
                    }
                )
            except Exception as e:
                logger.error(f"Error sending Telegram notification: {e}")
            
            return Response({'success': True, 'zayavka_id': zayavka.id})
            
        except Exception as e:
            logger.error(f"Error processing Mango incoming call: {e}")
            return Response({'error': 'Ошибка обработки звонка'}, status=500)

class MangoEmailProcessingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            # Обработка писем с записями от Mango Office
            data = request.data
            logger.info(f"Mango email processing data: {data}")
            
            # Здесь должна быть логика обработки писем
            # Например, привязка аудиозаписи к заявке
            
            return Response({'success': True})
            
        except Exception as e:
            logger.error(f"Error processing Mango email: {e}")
            return Response({'error': 'Ошибка обработки письма'}, status=500)
    def get(self, request):
        try:
            # Получение информации о письмах
            return Response({'status': 'ok'})
        except Exception as e:
            logger.error(f"Error getting Mango email info: {e}")
            return Response({'error': 'Ошибка получения информации'}, status=500) 