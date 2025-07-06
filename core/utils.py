from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для лучшего UX.
    """
    # Сначала вызываем стандартный обработчик
    response = exception_handler(exc, context)
    
    if response is not None:
        # Обрабатываем ошибки аутентификации
        if isinstance(exc, AuthenticationFailed):
            response.data = {
                'error': 'Необходима аутентификация',
                'code': 'AUTHENTICATION_REQUIRED',
                'detail': str(exc)
            }
            response.status_code = status.HTTP_401_UNAUTHORIZED
        
        # Обрабатываем ошибки прав доступа
        elif isinstance(exc, PermissionDenied):
            response.data = {
                'error': 'Недостаточно прав для выполнения операции',
                'code': 'PERMISSION_DENIED',
                'detail': str(exc)
            }
            response.status_code = status.HTTP_403_FORBIDDEN
        
        # Добавляем код ошибки для всех остальных ошибок
        else:
            if 'error' not in response.data:
                response.data = {
                    'error': 'Произошла ошибка',
                    'code': 'GENERAL_ERROR',
                    'detail': response.data
                }
    
    return response 

def download_audio_for_zayavka(zayavka_id, phone_number):
    """
    Простой и надежный скрипт для скачивания аудио из почты
    """
    import os
    import email
    import imaplib
    import logging
    import re
    from datetime import datetime, timedelta
    from email.header import decode_header
    from django.conf import settings
    from core.models import Zayavki, ZayavkaFile
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    
    try:
        # Получаем настройки почты
        email_settings = getattr(settings, 'MANGO_EMAIL_SETTINGS', {})
        email_address = email_settings.get('email')
        password = email_settings.get('password')
        imap_server = email_settings.get('imap_server', 'imap.gmail.com')
        imap_port = email_settings.get('imap_port', 993)
        download_dir = email_settings.get('download_dir', 'media/audio')
        
        logger.info(f'Начинаем скачивание аудио для заявки {zayavka_id}')
        logger.info(f'Email: {email_address}')
        logger.info(f'IMAP: {imap_server}:{imap_port}')
        logger.info(f'Папка: {download_dir}')
        
        if not email_address or not password:
            logger.error('Не настроены параметры почты')
            return False
            
        # Создаем папку
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        
        # Подключаемся к почте
        logger.info('Подключаемся к почтовому серверу...')
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select('INBOX')
        logger.info('Подключение успешно')
        
        # Ищем письма за последние 30 минут
        thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
        date_str = thirty_minutes_ago.strftime('%d-%b-%Y')
        
        logger.info(f'Ищем письма с {date_str}')
        
        # Простой поиск - все письма за последние 30 минут
        try:
            _, messages = mail.search(None, f'SINCE "{date_str}"')
            if not messages[0]:
                logger.info('Писем не найдено')
                mail.close()
                mail.logout()
                return False
                
            email_ids = messages[0].split()
            logger.info(f'Найдено писем: {len(email_ids)}')
            
        except Exception as e:
            logger.error(f'Ошибка поиска писем: {e}')
            mail.close()
            mail.logout()
            return False
        
        # Обрабатываем каждое письмо
        audio_found = False
        for email_id in email_ids:
            try:
                logger.info(f'Обрабатываем письмо {email_id}')
                
                # Получаем письмо
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                if not msg_data or not msg_data[0] or len(msg_data[0]) < 2:
                    continue
                    
                email_body = msg_data[0][1]
                if not isinstance(email_body, bytes):
                    continue
                    
                email_message = email.message_from_bytes(email_body)
                
                # Получаем тему и отправителя
                subject = email_message.get('Subject', '')
                from_email = email_message.get('From', '')
                
                logger.info(f'Тема: {subject}')
                logger.info(f'От: {from_email}')
                
                # Проверяем, что это от Mango Office
                if 'mango' not in from_email.lower() and 'recording' not in subject.lower():
                    logger.info('Пропускаем - не от Mango Office')
                    continue
                
                # Ищем вложения
                attachments = []
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                        
                    if part.get('Content-Disposition') is None:
                        continue
                        
                    filename = part.get_filename()
                    if filename:
                        # Декодируем имя файла
                        decoded_filename = decode_header(filename)
                        filename_parts = []
                        for part_name, encoding in decoded_filename:
                            if isinstance(part_name, bytes):
                                if encoding:
                                    filename_parts.append(part_name.decode(encoding))
                                else:
                                    filename_parts.append(part_name.decode('utf-8', errors='ignore'))
                            else:
                                filename_parts.append(part_name)
                        filename = ''.join(filename_parts)
                        
                        content = part.get_payload(decode=True)
                        attachments.append({
                            'filename': filename,
                            'content': content
                        })
                
                logger.info(f'Найдено вложений: {len(attachments)}')
                
                # Обрабатываем вложения
                for attachment in attachments:
                    filename = attachment['filename']
                    content = attachment['content']
                    
                    # Проверяем, что это аудиофайл
                    if not filename.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a', '.aac')):
                        logger.info(f'Пропускаем файл: {filename}')
                        continue
                    
                    logger.info(f'Найден аудиофайл: {filename}')
                    
                    # Проверяем номер телефона в имени файла
                    if phone_number and phone_number in filename:
                        logger.info(f'Номер телефона найден в файле: {phone_number}')
                        
                        # Сохраняем файл
                        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        name, ext = os.path.splitext(safe_filename)
                        safe_filename = f"{name}_{timestamp}{ext}"
                        
                        file_path = os.path.join(download_dir, safe_filename)
                        
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        
                        logger.info(f'Файл сохранен: {file_path}')
                        
                        # Создаем запись в базе
                        relative_path = file_path.replace('media/', '')
                        zayavka = Zayavki.objects.get(id=zayavka_id)
                        
                        ZayavkaFile.objects.create(
                            zayavka=zayavka,
                            file=relative_path,
                            type='audio'
                        )
                        
                        logger.info(f'Аудиофайл привязан к заявке {zayavka_id}')
                        audio_found = True
                        break
                    else:
                        logger.info(f'Номер телефона {phone_number} не найден в файле {filename}')
                
                if audio_found:
                    break
                    
            except Exception as e:
                logger.error(f'Ошибка при обработке письма {email_id}: {e}')
                continue
        
        mail.close()
        mail.logout()
        
        if audio_found:
            logger.info(f'Аудиофайл успешно скачан для заявки {zayavka_id}')
        else:
            logger.info(f'Аудиофайл для заявки {zayavka_id} не найден')
        
        return audio_found
        
    except Exception as e:
        logger.error(f'Ошибка при скачивании аудио: {e}')
        return False

# Старые функции удалены - теперь все в одной функции download_audio_for_zayavka 

# Telegram Alerts
import requests
import logging
from django.conf import settings
from typing import Optional, Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def send_telegram_alert(
    message: str, 
    token: Optional[str] = None, 
    chat_id: Optional[str] = None,
    parse_mode: str = "HTML"
) -> bool:
    """
    Отправляет сообщение в Telegram
    
    Args:
        message: Текст сообщения
        token: Токен бота (если не указан, берется из настроек)
        chat_id: ID чата (если не указан, берется из настроек)
        parse_mode: Режим парсинга (HTML или Markdown)
    
    Returns:
        bool: True если сообщение отправлено успешно, False в противном случае
    """
    try:
        # Получаем настройки из переменных окружения или settings
        bot_token = token or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = chat_id or getattr(settings, 'TELEGRAM_CHAT_ID', None)
        
        if not bot_token or not chat_id:
            logger.error("Telegram bot token or chat_id not configured")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        # Безопасное логирование без эмодзи для Windows
        safe_message = message.replace('🔐', '[LOGIN]').replace('⏰', '[TIME]').replace('📄', '[DESC]').replace('👤', '[USER]')
        logger.info(f"Telegram alert sent successfully: {safe_message[:100]}...")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Telegram alert: {e}")
        return False

def format_error_alert(
    error: Exception,
    request_path: str = "",
    user_info: str = "",
    additional_info: Dict[str, Any] = None
) -> str:
    """
    Форматирует сообщение об ошибке для Telegram
    
    Args:
        error: Объект исключения
        request_path: Путь запроса
        user_info: Информация о пользователе
        additional_info: Дополнительная информация
    
    Returns:
        str: Отформатированное сообщение
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"🚨 <b>ОШИБКА В CRM</b>\n\n"
    message += f"⏰ <b>Время:</b> {timestamp}\n"
    message += f"❌ <b>Ошибка:</b> {type(error).__name__}: {str(error)}\n"
    
    if request_path:
        message += f"🔗 <b>Путь:</b> {request_path}\n"
    
    if user_info:
        message += f"👤 <b>Пользователь:</b> {user_info}\n"
    
    if additional_info:
        message += f"\n📋 <b>Дополнительно:</b>\n"
        for key, value in additional_info.items():
            message += f"• {key}: {value}\n"
    
    return message

def format_business_alert(
    event_type: str,
    description: str,
    user_info: str = "",
    additional_data: Dict[str, Any] = None
) -> str:
    """
    Форматирует бизнес-событие для Telegram
    
    Args:
        event_type: Тип события
        description: Описание события
        user_info: Информация о пользователе
        additional_data: Дополнительные данные
    
    Returns:
        str: Отформатированное сообщение
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Эмодзи для разных типов событий
    emoji_map = {
        "new_zayavka": "📝",
        "payment": "💰",
        "login": "🔐",
        "error": "🚨",
        "warning": "⚠️",
        "info": "ℹ️",
        "success": "✅"
    }
    
    emoji = emoji_map.get(event_type, "📢")
    
    message = f"{emoji} <b>{event_type.upper().replace('_', ' ')}</b>\n\n"
    message += f"⏰ <b>Время:</b> {timestamp}\n"
    message += f"📄 <b>Описание:</b> {description}\n"
    
    if user_info:
        message += f"👤 <b>Пользователь:</b> {user_info}\n"
    
    if additional_data:
        message += f"\n📋 <b>Детали:</b>\n"
        for key, value in additional_data.items():
            if isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False, indent=2)
            message += f"• {key}: {value}\n"
    
    return message

def send_error_alert(
    error: Exception,
    request_path: str = "",
    user_info: str = "",
    additional_info: Dict[str, Any] = None
) -> bool:
    """
    Отправляет алерт об ошибке в Telegram
    
    Args:
        error: Объект исключения
        request_path: Путь запроса
        user_info: Информация о пользователе
        additional_info: Дополнительная информация
    
    Returns:
        bool: True если сообщение отправлено успешно
    """
    message = format_error_alert(error, request_path, user_info, additional_info)
    return send_telegram_alert(message)

def send_business_alert(
    event_type: str,
    description: str,
    user_info: str = "",
    additional_data: Dict[str, Any] = None
) -> bool:
    """
    Отправляет бизнес-событие в Telegram
    
    Args:
        event_type: Тип события
        description: Описание события
        user_info: Информация о пользователе
        additional_data: Дополнительные данные
    
    Returns:
        bool: True если сообщение отправлено успешно
    """
    message = format_business_alert(event_type, description, user_info, additional_data)
    return send_telegram_alert(message) 