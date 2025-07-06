from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = '8032155601:AAG9myXmM3tO12LRFsX9T64wVIEdi6pexi8'
TELEGRAM_CHAT_ID = 1802367546

# MasterFeedbackView
# (перенести соответствующий класс из views.py) 

class MasterFeedbackView(APIView):
    permission_classes = []
    def post(self, request):
        try:
            # Получаем данные обратной связи
            data = request.data
            logger.info(f"Master feedback received: {data}")
            
            # Извлекаем информацию
            master_name = data.get('master_name', 'Не указано')
            phone = data.get('phone', 'Не указано')
            message = data.get('message', 'Не указано')
            rating = data.get('rating', 'Не указано')
            
            # Формируем сообщение для Telegram
            telegram_message = f"""
📝 Обратная связь от мастера

👤 Мастер: {master_name}
📞 Телефон: {phone}
⭐ Оценка: {rating}
💬 Сообщение: {message}

⏰ Время: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            # Отправляем в Telegram
            try:
                response = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    data={
                        'chat_id': TELEGRAM_CHAT_ID,
                        'text': telegram_message,
                        'parse_mode': 'HTML'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info("Feedback sent to Telegram successfully")
                    return Response({
                        'success': True,
                        'message': 'Обратная связь отправлена успешно'
                    })
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return Response({
                        'success': False,
                        'message': 'Ошибка отправки в Telegram'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Telegram request failed: {e}")
                return Response({
                    'success': False,
                    'message': 'Ошибка подключения к Telegram'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Error processing master feedback: {e}")
            return Response({
                'success': False,
                'message': 'Ошибка обработки обратной связи'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 