import os
import email
import imaplib
import logging
import re
from datetime import datetime
from email.header import decode_header
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Zayavki, Tranzakcii
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Обрабатывает письма с записями от Mango Office'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email адрес для проверки писем'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Пароль от email'
        )
        parser.add_argument(
            '--imap-server',
            type=str,
            default='imap.gmail.com',
            help='IMAP сервер (по умолчанию: imap.gmail.com)'
        )
        parser.add_argument(
            '--imap-port',
            type=int,
            default=993,
            help='IMAP порт (по умолчанию: 993)'
        )
        parser.add_argument(
            '--download-dir',
            type=str,
            default='media/audio',
            help='Папка для сохранения аудиофайлов'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Режим тестирования без сохранения файлов'
        )

    def handle(self, *args, **options):
        email_address = options['email']
        password = options['password']
        imap_server = options['imap_server']
        imap_port = options['imap_port']
        download_dir = options['download_dir']
        dry_run = options['dry_run']

        if not email_address or not password:
            self.stdout.write(
                self.style.ERROR('Необходимо указать email и пароль')
            )
            return

        self.stdout.write('Начинаем обработку писем от Mango Office...')
        self.stdout.write(f'Подключение к {imap_server}:{imap_port}')
        
        try:
            # Создаем папку для аудиофайлов
            if not dry_run:
                Path(download_dir).mkdir(parents=True, exist_ok=True)

            # Подключаемся к почтовому серверу
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(email_address, password)
            
            # Выбираем папку INBOX
            mail.select('INBOX')
            
            # Сначала проверим общее количество писем
            _, messages = mail.search(None, 'ALL')
            total_emails = len(messages[0].split()) if messages[0] else 0
            self.stdout.write(f'Всего писем в ящике: {total_emails}')
            
            # Ищем письма с вложениями (аудиофайлами) - только для поддерживаемых серверов
            emails_with_attachments = 0
            try:
                _, messages_with_attachments = mail.search(None, 'HASATTACH')
                emails_with_attachments = len(messages_with_attachments[0].split()) if messages_with_attachments[0] else 0
                self.stdout.write(f'Писем с вложениями: {emails_with_attachments}')
            except Exception as e:
                self.stdout.write(f'Сервер не поддерживает HASATTACH, пропускаем: {e}')
            
            # Ищем письма от Mango Office (расширенный поиск)
            mango_filters = [
                'FROM "auto-mailer@mangotele.com"',
                'FROM "mango-office.ru"',
                'FROM "mango-office.com"', 
                'FROM "mango.ru"',
                'SUBJECT "recording"',
                'SUBJECT "call"'
            ]
            
            found_emails = []
            for filter_query in mango_filters:
                try:
                    _, messages = mail.search(None, filter_query)
                    if messages[0]:
                        email_ids = messages[0].split()
                        found_emails.extend(email_ids)
                        self.stdout.write(f'Найдено писем по фильтру "{filter_query}": {len(email_ids)}')
                except Exception as e:
                    self.stdout.write(f'Ошибка при поиске по фильтру "{filter_query}": {e}')
            
            # Убираем дубликаты
            found_emails = list(set(found_emails))
            self.stdout.write(f'Всего уникальных писем от Mango Office: {len(found_emails)}')
            
            if not found_emails:
                self.stdout.write('Писем от Mango Office не найдено')
                self.stdout.write('Попробуйте проверить:')
                self.stdout.write('1. Правильность email адреса')
                self.stdout.write('2. Настройки отправки в Mango Office')
                self.stdout.write('3. Наличие писем с вложениями в ящике')
                return

            processed_count = 0
            for email_id in found_emails:
                try:
                    # Получаем письмо
                    _, msg_data = mail.fetch(email_id, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Обрабатываем письмо
                    if self.process_email(email_message, download_dir, dry_run):
                        processed_count += 1
                    
                except Exception as e:
                    logger.error(f'Ошибка при обработке письма {email_id}: {e}')
                    self.stdout.write(f'Ошибка при обработке письма {email_id}: {e}')
                    continue

            mail.close()
            mail.logout()
            
            self.stdout.write(
                self.style.SUCCESS(f'Обработка писем завершена. Обработано: {processed_count}')
            )
            
        except Exception as e:
            logger.error(f'Ошибка при подключении к почте: {e}')
            self.stdout.write(
                self.style.ERROR(f'Ошибка: {e}')
            )

    def process_email(self, email_message, download_dir, dry_run):
        """Обрабатывает отдельное письмо от Mango Office"""
        
        # Получаем информацию о письме
        subject = self.get_email_subject(email_message)
        from_email = self.get_email_from(email_message)
        
        self.stdout.write(f'Обрабатываем письмо: {subject}')
        self.stdout.write(f'От: {from_email}')
        
        # Проверяем, что это письмо от Mango Office (расширенная проверка)
        mango_domains = ['mangotele.com', 'mango-office.ru', 'mango-office.com', 'mango.ru']
        is_mango_email = any(domain in from_email.lower() for domain in mango_domains)
        
        # Также проверяем тему письма
        subject_lower = subject.lower()
        mango_keywords = ['запись', 'recording', 'звонок', 'call', 'mango']
        has_mango_keywords = any(keyword in subject_lower for keyword in mango_keywords)
        
        if not is_mango_email and not has_mango_keywords:
            self.stdout.write(f'Пропускаем письмо (не от Mango Office): {subject}')
            return False
        
        # Ищем вложения (аудиофайлы)
        attachments = self.get_attachments(email_message)
        self.stdout.write(f'Найдено вложений: {len(attachments)}')
        
        audio_files_found = 0
        for attachment in attachments:
            filename = attachment['filename']
            content = attachment['content']
            
            # Проверяем, что это аудиофайл
            if not self.is_audio_file(filename):
                self.stdout.write(f'Пропускаем файл (не аудио): {filename}')
                continue
                
            self.stdout.write(f'Найден аудиофайл: {filename}')
            audio_files_found += 1
            
            # Извлекаем информацию о звонке из имени файла или темы
            call_info = self.extract_call_info(filename, subject)
            
            if not dry_run:
                # Сохраняем файл
                file_path = self.save_audio_file(filename, content, download_dir)
                
                # Создаем запись файла для записи
                self.create_audio_file(file_path, call_info)
            else:
                self.stdout.write(f'DRY RUN: Файл {filename} будет сохранен')

        return audio_files_found > 0

    def get_email_subject(self, email_message):
        """Извлекает тему письма"""
        subject = email_message.get('Subject', '')
        if subject:
            decoded_subject = decode_header(subject)
            subject_parts = []
            for part, encoding in decoded_subject:
                if isinstance(part, bytes):
                    if encoding:
                        subject_parts.append(part.decode(encoding))
                    else:
                        subject_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    subject_parts.append(part)
            return ''.join(subject_parts)
        return ''

    def get_email_from(self, email_message):
        """Извлекает адрес отправителя"""
        from_header = email_message.get('From', '')
        if from_header:
            decoded_from = decode_header(from_header)
            from_parts = []
            for part, encoding in decoded_from:
                if isinstance(part, bytes):
                    if encoding:
                        from_parts.append(part.decode(encoding))
                    else:
                        from_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    from_parts.append(part)
            return ''.join(from_parts)
        return ''

    def get_attachments(self, email_message):
        """Извлекает вложения из письма"""
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
        
        return attachments

    def is_audio_file(self, filename):
        """Проверяет, является ли файл аудиофайлом"""
        audio_extensions = ['.wav', '.mp3', '.ogg', '.m4a', '.aac']
        return any(filename.lower().endswith(ext) for ext in audio_extensions)

    def extract_call_info(self, filename, subject):
        """Извлекает информацию о звонке из имени файла или темы"""
        # Здесь можно добавить логику извлечения информации
        # Например, номер телефона, дату, время и т.д.
        call_info = {
            'filename': filename,
            'subject': subject,
            'phone_number': None,
            'call_date': None,
            'call_time': None
        }
        
        # Попытка извлечь номер телефона из имени файла
        phone_pattern = r'(\+?7\d{10})'
        phone_match = re.search(phone_pattern, filename)
        if phone_match:
            call_info['phone_number'] = phone_match.group(1)
        
        # Попытка извлечь дату и время
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        date_match = re.search(date_pattern, filename)
        if date_match:
            call_info['call_date'] = date_match.group(1)
        
        return call_info

    def save_audio_file(self, filename, content, download_dir):
        """Сохраняет аудиофайл на диск"""
        # Создаем безопасное имя файла
        safe_filename = self.get_safe_filename(filename)
        file_path = os.path.join(download_dir, safe_filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        self.stdout.write(f'Файл сохранен: {file_path}')
        return file_path

    def get_safe_filename(self, filename):
        """Создает безопасное имя файла"""
        # Убираем небезопасные символы
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Добавляем временную метку для уникальности
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(safe_filename)
        return f"{name}_{timestamp}{ext}"

    def create_audio_file(self, file_path, call_info):
        """Создает запись файла для аудиозаписи"""
        try:
            # Ищем заявку по номеру телефона
            zayavka = None
            if call_info['phone_number']:
                zayavka = Zayavki.objects.filter(
                    phone_client__icontains=call_info['phone_number']
                ).first()
                
                if zayavka:
                    self.stdout.write(f'Найдена заявка: {zayavka.id} для номера {call_info["phone_number"]}')
                else:
                    self.stdout.write(f'Заявка для номера {call_info["phone_number"]} не найдена')
            
            # Создаем запись файла
            from core.models import ZayavkaFile
            
            # Создаем относительный путь для FileField
            relative_path = file_path.replace('media/', '')
            
            zayavka_file = ZayavkaFile.objects.create(
                zayavka=zayavka,
                file=relative_path,
                type='audio'
            )
            
            self.stdout.write(f'Создана запись файла: {zayavka_file.id}')
            
        except Exception as e:
            logger.error(f'Ошибка при создании записи файла: {e}')
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании записи файла: {e}')
            ) 