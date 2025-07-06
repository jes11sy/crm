#!/usr/bin/env python3
"""
Мониторинг почты для скачивания аудиозаписей от Mango Office
"""

import os
import sys
import time
import imaplib
import email
import re
import json
from datetime import datetime, timedelta
from email.header import decode_header

# Добавляем путь к Django проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')

import django
django.setup()

from core.models import Zayavki, ZayavkaFile
from django.conf import settings

# Настройки почты
EMAIL = "recordmango1@rambler.ru"
PASSWORD = os.environ.get('MANGO_EMAIL_PASSWORD')
if not PASSWORD:
    raise ValueError("MANGO_EMAIL_PASSWORD environment variable is required")
IMAP_SERVER = "imap.rambler.ru"
IMAP_PORT = 993

# Папка для сохранения аудиофайлов
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_files')
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Файл для отслеживания обработанных писем
PROCESSED_EMAILS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed_emails.json')

def load_processed_emails():
    """Загружаем список обработанных писем"""
    try:
        if os.path.exists(PROCESSED_EMAILS_FILE):
            with open(PROCESSED_EMAILS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()
    except Exception as e:
        log_message(f"Ошибка загрузки обработанных писем: {e}")
        return set()

def save_processed_emails(processed_emails):
    """Сохраняем список обработанных писем"""
    try:
        with open(PROCESSED_EMAILS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(processed_emails), f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_message(f"Ошибка сохранения обработанных писем: {e}")

def log_message(message):
    """Логирование с временной меткой"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def download_attachment(part, filename):
    """Скачивание вложения"""
    try:
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Проверяем, не скачан ли уже файл
        if os.path.exists(filepath):
            log_message(f"Файл уже существует: {filename}")
            return filepath
        
        # Скачиваем файл
        with open(filepath, 'wb') as f:
            f.write(part.get_payload(decode=True))
        
        log_message(f"Скачан файл: {filename}")
        return filepath
        
    except Exception as e:
        log_message(f"Ошибка скачивания {filename}: {e}")
        return None

def check_file_exists_in_db(filename, call_time=None):
    """Проверяем, есть ли уже запись в БД по имени файла и времени звонка"""
    try:
        # Сначала проверяем по имени файла
        existing_file = ZayavkaFile.objects.filter(
            file__icontains=filename,
            type='audio'
        ).first()
        
        if existing_file:
            log_message(f"Файл уже есть в БД: {filename}")
            return True
        
        # Если есть время звонка, проверяем по номеру и времени
        if call_time:
            # Извлекаем номер телефона из имени файла
            phone_pattern = r'(\+?7\d{10})'
            match = re.search(phone_pattern, filename)
            if match:
                phone = match.group(1)
                if phone.startswith('+'):
                    phone = phone[1:]
                
                # Ищем заявки с этим номером за последние 30 минут от времени звонка
                time_window_start = call_time - timedelta(minutes=30)
                time_window_end = call_time + timedelta(minutes=30)
                
                existing_zayavka = Zayavki.objects.filter(
                    phone_client=phone,
                    meeting_date__range=(time_window_start, time_window_end)
                ).first()
                
                if existing_zayavka:
                    # Проверяем, есть ли уже аудиофайл для этой заявки в это время
                    existing_audio = ZayavkaFile.objects.filter(
                        zayavka=existing_zayavka,
                        type='audio',
                        uploaded_at__range=(time_window_start, time_window_end)
                    ).first()
                    
                    if existing_audio:
                        log_message(f"Аудио для звонка {phone} в {call_time} уже есть в БД")
                        return True
        
        return False
        
    except Exception as e:
        log_message(f"Ошибка проверки файла в БД: {e}")
        return False

def extract_call_time_from_filename(filename):
    """Извлекаем время звонка из имени файла"""
    try:
        # Паттерны для разных форматов времени в имени файла
        patterns = [
            r'(\d{4})\.(\d{2})\.(\d{2})__(\d{2})-(\d{2})-(\d{2})',  # 2025.07.05__17-16-36
            r'(\d{2})\.(\d{2})\.(\d{4})_(\d{2}):(\d{2}):(\d{2})',  # 05.07.2025_17:16:36
            r'(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})',    # 2025-07-05_17-16-36
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                if len(match.groups()) == 6:
                    if pattern == patterns[0]:  # 2025.07.05__17-16-36
                        year, month, day, hour, minute, second = match.groups()
                    elif pattern == patterns[1]:  # 05.07.2025_17:16:36
                        day, month, year, hour, minute, second = match.groups()
                    else:  # 2025-07-05_17-16-36
                        year, month, day, hour, minute, second = match.groups()
                    
                    try:
                        call_time = datetime(
                            int(year), int(month), int(day),
                            int(hour), int(minute), int(second)
                        )
                        log_message(f"Извлечено время звонка: {call_time}")
                        return call_time
                    except ValueError:
                        continue
        
        log_message(f"Не удалось извлечь время из имени файла: {filename}")
        return None
        
    except Exception as e:
        log_message(f"Ошибка извлечения времени: {e}")
        return None

def find_zayavka_by_phone(phone):
    """Поиск заявки по номеру телефона"""
    try:
        # Убираем + если есть
        if phone.startswith('+'):
            phone = phone[1:]
        
        # Ищем заявку
        zayavka = Zayavki.objects.filter(phone_client=phone).first()
        
        if zayavka:
            log_message(f"Найдена заявка для номера {phone}: ID {zayavka.id}")
            return zayavka
        else:
            log_message(f"Заявка для номера {phone} не найдена")
            return None
            
    except Exception as e:
        log_message(f"Ошибка поиска заявки для {phone}: {e}")
        return None

def process_email():
    """Обработка писем"""
    # Загружаем список уже обработанных писем
    processed_emails = load_processed_emails()
    
    try:
        log_message("Подключение к почте...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        mail.select('INBOX')
        
        # Ищем письма за последние 2 часа
        two_hours_ago = datetime.now() - timedelta(hours=2)
        date_str = two_hours_ago.strftime('%d-%b-%Y')
        _, messages = mail.search(None, f'SINCE "{date_str}"')
        
        if not messages[0]:
            log_message("Новых писем не найдено")
            mail.close()
            mail.logout()
            return
        
        email_ids = messages[0].split()
        log_message(f"Найдено писем: {len(email_ids)}")
        
        processed_count = 0
        skipped_count = 0
        
        for email_id in email_ids:
            email_id_str = email_id.decode('utf-8')
            
            # Проверяем, не обрабатывали ли уже это письмо
            if email_id_str in processed_emails:
                log_message(f"Письмо {email_id_str} уже обработано, пропускаем")
                skipped_count += 1
                continue
            
            try:
                # Получаем письмо
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                if not msg_data or not msg_data[0] or len(msg_data[0]) < 2:
                    continue
                
                email_body = msg_data[0][1]
                if not isinstance(email_body, bytes):
                    continue
                
                email_message = email.message_from_bytes(email_body)
                
                # Проверяем, от Mango ли это
                from_email = email_message.get('From', '')
                subject = email_message.get('Subject', '')
                
                is_mango = False
                if 'mango' in from_email.lower():
                    is_mango = True
                elif 'recording' in subject.lower() or 'запись' in subject.lower():
                    is_mango = True
                
                if not is_mango:
                    # Добавляем в обработанные, чтобы не проверять снова
                    processed_emails.add(email_id_str)
                    continue
                
                log_message(f"Обрабатываем письмо от Mango: {subject}")
                
                has_audio = False
                
                # Ищем вложения
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    
                    if part.get('Content-Disposition') is None:
                        continue
                    
                    filename = part.get_filename()
                    if not filename:
                        continue
                    
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
                    
                    # Проверяем, аудио ли это
                    if not filename.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a', '.aac')):
                        continue
                    
                    has_audio = True
                    log_message(f"Найден аудиофайл: {filename}")
                    
                    # Извлекаем время звонка из имени файла
                    call_time = extract_call_time_from_filename(filename)
                    
                    # Ищем номер телефона в имени файла
                    phone_pattern = r'(\+?7\d{10})'
                    match = re.search(phone_pattern, filename)
                    if not match:
                        log_message(f"Номер телефона не найден в {filename}")
                        continue
                    
                    phone = match.group(1)
                    log_message(f"Извлечен номер: {phone}")
                    
                    # Проверяем, не обработан ли уже файл
                    if check_file_exists_in_db(filename, call_time):
                        log_message(f"Файл уже есть в БД, пропускаем: {filename}")
                        continue
                    
                    # Ищем заявку с учетом времени звонка
                    zayavka = None
                    if call_time:
                        # Ищем заявку в окне ±30 минут от времени звонка
                        time_window_start = call_time - timedelta(minutes=30)
                        time_window_end = call_time + timedelta(minutes=30)
                        
                        zayavka = Zayavki.objects.filter(
                            phone_client=phone,
                            meeting_date__range=(time_window_start, time_window_end)
                        ).first()
                        
                        if zayavka:
                            log_message(f"Найдена заявка для звонка {phone} в {call_time}: ID {zayavka.id}")
                        else:
                            log_message(f"Заявка для звонка {phone} в {call_time} не найдена, пропускаем файл")
                            continue
                    else:
                        # Если не удалось извлечь время, ищем по номеру без учета времени
                        zayavka = find_zayavka_by_phone(phone)
                        if not zayavka:
                            log_message(f"Заявка для номера {phone} не найдена, пропускаем файл")
                            continue
                    
                    # Скачиваем файл только если найдена заявка
                    filepath = download_attachment(part, filename)
                    if not filepath:
                        continue
                    
                    # Сохраняем в БД только имя файла, а не абсолютный путь
                    filename_only = os.path.basename(filepath)

                    # Создаем запись в ZayavkaFile
                    try:
                        zayavka_file = ZayavkaFile.objects.create(
                            zayavka=zayavka,
                            file=filename_only,
                            type='audio'
                        )
                        log_message(f"Создана запись ZayavkaFile: ID {zayavka_file.id}")
                        
                    except Exception as e:
                        log_message(f"Ошибка создания ZayavkaFile: {e}")
                
                # Если письмо от Mango и содержит аудио, считаем его обработанным
                if is_mango and has_audio:
                    processed_count += 1
                
                # Добавляем письмо в список обработанных
                processed_emails.add(email_id_str)
                
            except Exception as e:
                log_message(f"Ошибка обработки письма: {e}")
        
        # Сохраняем обновленный список обработанных писем
        save_processed_emails(processed_emails)
        
        log_message(f"Обработано новых писем: {processed_count}")
        log_message(f"Пропущено уже обработанных: {skipped_count}")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        log_message(f"Ошибка подключения к почте: {e}")

def main():
    """Основная функция"""
    log_message("=== МОНИТОРИНГ ПОЧТЫ Mango Office ЗАПУЩЕН ===")
    log_message(f"Папка для аудиофайлов: {AUDIO_DIR}")
    log_message(f"Файл отслеживания: {PROCESSED_EMAILS_FILE}")
    log_message("Нажмите Ctrl+C для остановки")
    print()
    
    try:
        while True:
            process_email()
            log_message("Ожидание 10 секунд...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        log_message("Мониторинг остановлен пользователем")
    except Exception as e:
        log_message(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 