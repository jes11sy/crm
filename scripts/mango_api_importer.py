#!/usr/bin/env python3
"""
Скрипт для интеграции с API Mango Office и загрузки аудиозаписей разговоров
"""

import os
import sys
import requests
import hashlib
import hmac
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from django.conf import settings
from core.models import Zayavki, ZayavkaFile, Polzovateli

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mango_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MangoAPIImporter:
    def __init__(self, api_key, api_salt, system_user_login='admin'):
        """
        Инициализация импортера Mango Office API
        
        Args:
            api_key (str): API ключ от Mango Office
            api_salt (str): API соль от Mango Office
            system_user_login (str): Логин системного пользователя для прикрепления файлов
        """
        self.api_key = api_key
        self.api_salt = api_salt
        self.base_url = "https://app.mango-office.ru/vpbx"
        self.system_user = self._get_system_user(system_user_login)
        self.download_dir = Path('downloads/mango_audio')
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_system_user(self, login):
        """Получение системного пользователя"""
        try:
            return Polzovateli.objects.get(login=login)
        except Polzovateli.DoesNotExist:
            logger.error(f"Системный пользователь {login} не найден")
            sys.exit(1)
    
    def _generate_signature(self, data):
        """
        Генерация подписи для API запросов Mango Office
        """
        # Сортируем ключи
        sorted_keys = sorted(data.keys())
        
        # Формируем строку для подписи
        sign_string = self.api_salt
        for key in sorted_keys:
            sign_string += str(data[key])
        sign_string += self.api_salt
        
        # Создаем подпись
        signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()
        return signature
    
    def _make_api_request(self, method, params=None):
        """
        Выполнение запроса к API Mango Office
        
        Args:
            method (str): Метод API
            params (dict): Параметры запроса
            
        Returns:
            dict: Ответ от API
        """
        if params is None:
            params = {}
        
        # Добавляем обязательные параметры
        params.update({
            'vpbx_api_key': self.api_key,
            'vpbx_api_salt': self.api_salt,
        })
        
        # Генерируем подпись
        signature = self._generate_signature(params)
        params['signature'] = signature
        
        try:
            url = f"{self.base_url}/{method}"
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('result') == '0':
                logger.error(f"API ошибка: {result.get('message', 'Неизвестная ошибка')}")
                return None
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON ответа: {e}")
            return None
    
    def get_calls_history(self, date_from=None, date_to=None, limit=100):
        """
        Получение истории звонков
        
        Args:
            date_from (str): Дата начала в формате YYYY-MM-DD
            date_to (str): Дата окончания в формате YYYY-MM-DD
            limit (int): Количество записей
            
        Returns:
            list: Список звонков
        """
        if date_from is None:
            date_from = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if date_to is None:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit
        }
        
        logger.info(f"Получение истории звонков с {date_from} по {date_to}")
        result = self._make_api_request('stats/request', params)
        
        if result and 'data' in result:
            calls = result['data']
            logger.info(f"Получено {len(calls)} звонков")
            return calls
        
        return []
    
    def get_call_records(self, call_id):
        """
        Получение информации о записи разговора
        
        Args:
            call_id (str): ID звонка
            
        Returns:
            dict: Информация о записи
        """
        params = {
            'call_id': call_id
        }
        
        result = self._make_api_request('queries/request', params)
        
        if result and 'data' in result:
            return result['data']
        
        return None
    
    def download_audio_file(self, url, filename):
        """
        Загрузка аудиофайла
        
        Args:
            url (str): URL для загрузки файла
            filename (str): Имя файла для сохранения
            
        Returns:
            Path: Путь к загруженному файлу или None при ошибке
        """
        try:
            file_path = self.download_dir / filename
            
            # Проверяем, не загружен ли уже файл
            if file_path.exists():
                logger.info(f"Файл уже существует: {filename}")
                return file_path
            
            # Загружаем файл
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Файл загружен: {filename}")
            return file_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка загрузки файла {filename}: {e}")
            return None
    
    def extract_phone_from_call(self, call_data):
        """
        Извлечение номера телефона из данных звонка
        
        Args:
            call_data (dict): Данные звонка
            
        Returns:
            str: Номер телефона или None
        """
        # Пытаемся найти номер в различных полях
        phone_fields = ['from_extension', 'to_extension', 'from_number', 'to_number']
        
        for field in phone_fields:
            if field in call_data and call_data[field]:
                phone = str(call_data[field])
                # Очищаем номер от лишних символов
                phone = ''.join(filter(str.isdigit, phone))
                
                # Нормализуем номер
                if len(phone) == 11 and phone.startswith('8'):
                    phone = '+7' + phone[1:]
                elif len(phone) == 11 and phone.startswith('7'):
                    phone = '+' + phone
                elif len(phone) == 10:
                    phone = '+7' + phone
                
                if len(phone) >= 10:
                    return phone
        
        return None
    
    def find_zayavka_by_phone(self, phone):
        """
        Поиск заявки по номеру телефона
        
        Args:
            phone (str): Номер телефона
            
        Returns:
            Zayavki: Заявка или None
        """
        # Нормализация номера для поиска
        search_phone = phone
        if phone.startswith('+7'):
            search_phone = phone[2:]  # Убираем +7 для поиска
        
        # Поиск по номеру клиента
        zayavka = Zayavki.objects.filter(
            phone_client__icontains=search_phone
        ).first()
        
        if not zayavka:
            # Поиск по номеру АТС
            zayavka = Zayavki.objects.filter(
                phone_atc__icontains=search_phone
            ).first()
        
        return zayavka
    
    def attach_audio_to_zayavka(self, file_path, zayavka, call_data):
        """
        Прикрепление аудиофайла к заявке
        
        Args:
            file_path (Path): Путь к аудиофайлу
            zayavka (Zayavki): Заявка
            call_data (dict): Данные звонка
            
        Returns:
            bool: Успех операции
        """
        try:
            from django.core.files import File
            from django.core.files.temp import NamedTemporaryFile
            from django.db import transaction
            
            with transaction.atomic():
                # Проверяем, нет ли уже такого файла
                existing_file = ZayavkaFile.objects.filter(
                    zayavka=zayavka,
                    type='audio',
                    file__endswith=file_path.name
                ).first()
                
                if existing_file:
                    logger.info(f"Файл уже прикреплен: {file_path.name} к заявке {zayavka.id}")
                    return True
                
                # Создаем временный файл для Django
                with NamedTemporaryFile(delete=False) as temp_file:
                    # Копируем содержимое
                    with open(file_path, 'rb') as source_file:
                        temp_file.write(source_file.read())
                    temp_file.flush()
                    
                    # Создаем запись в БД
                    zayavka_file = ZayavkaFile.objects.create(
                        zayavka=zayavka,
                        type='audio',
                        uploaded_by=self.system_user
                    )
                    
                    # Прикрепляем файл
                    zayavka_file.file.save(
                        file_path.name,
                        File(open(temp_file.name, 'rb')),
                        save=True
                    )
                    
                    # Удаляем временный файл
                    os.unlink(temp_file.name)
                
                logger.info(f"Аудио прикреплено: {file_path.name} к заявке {zayavka.id} ({zayavka.client_name})")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка прикрепления файла {file_path}: {e}")
            return False
    
    def process_calls(self, date_from=None, date_to=None, dry_run=False):
        """
        Обработка звонков и загрузка аудиозаписей
        
        Args:
            date_from (str): Дата начала
            date_to (str): Дата окончания
            dry_run (bool): Режим тестирования
        """
        logger.info("Начинаем обработку звонков Mango Office")
        
        # Получаем историю звонков
        calls = self.get_calls_history(date_from, date_to)
        
        if not calls:
            logger.warning("Звонки не найдены")
            return
        
        processed_count = 0
        downloaded_count = 0
        attached_count = 0
        error_count = 0
        
        for call in calls:
            processed_count += 1
            
            try:
                # Извлекаем номер телефона
                phone = self.extract_phone_from_call(call)
                
                if not phone:
                    logger.warning(f"Не удалось извлечь номер из звонка {call.get('id', 'unknown')}")
                    error_count += 1
                    continue
                
                # Ищем заявку
                zayavka = self.find_zayavka_by_phone(phone)
                
                if not zayavka:
                    logger.warning(f"Заявка не найдена для номера {phone} (звонок: {call.get('id', 'unknown')})")
                    error_count += 1
                    continue
                
                # Проверяем, есть ли запись разговора
                if not call.get('record_url'):
                    logger.info(f"Запись разговора отсутствует для звонка {call.get('id', 'unknown')}")
                    continue
                
                # Формируем имя файла
                call_id = call.get('id', 'unknown')
                timestamp = call.get('start', '')
                filename = f"mango_{call_id}_{timestamp}_{phone}.mp3"
                
                if dry_run:
                    logger.info(f"[DRY RUN] Найдена заявка {zayavka.id} для {phone} - {filename}")
                    downloaded_count += 1
                    attached_count += 1
                else:
                    # Загружаем аудиофайл
                    file_path = self.download_audio_file(call['record_url'], filename)
                    
                    if file_path:
                        downloaded_count += 1
                        
                        # Прикрепляем к заявке
                        if self.attach_audio_to_zayavka(file_path, zayavka, call):
                            attached_count += 1
                        else:
                            error_count += 1
                    else:
                        error_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка обработки звонка {call.get('id', 'unknown')}: {e}")
                error_count += 1
        
        logger.info(f"Обработка завершена:")
        logger.info(f"  Обработано звонков: {processed_count}")
        logger.info(f"  Загружено файлов: {downloaded_count}")
        logger.info(f"  Прикреплено к заявкам: {attached_count}")
        logger.info(f"  Ошибок: {error_count}")

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Импорт аудиозаписей из Mango Office API')
    parser.add_argument('--api-key', required=True, help='API ключ Mango Office')
    parser.add_argument('--api-salt', required=True, help='API соль Mango Office')
    parser.add_argument('--system-user', default='admin', help='Логин системного пользователя')
    parser.add_argument('--date-from', help='Дата начала (YYYY-MM-DD)')
    parser.add_argument('--date-to', help='Дата окончания (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true', help='Режим тестирования')
    
    args = parser.parse_args()
    
    # Создаем папку для логов
    Path('logs').mkdir(exist_ok=True)
    
    importer = MangoAPIImporter(args.api_key, args.api_salt, args.system_user)
    
    if args.dry_run:
        logger.info("Запуск в режиме DRY RUN - изменения не будут сохранены")
    
    importer.process_calls(args.date_from, args.date_to, args.dry_run)

if __name__ == '__main__':
    main() 