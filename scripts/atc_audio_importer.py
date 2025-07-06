#!/usr/bin/env python3
"""
Скрипт для автоматической загрузки аудиозаписей из АТС и прикрепления к заявкам
"""

import os
import sys
import re
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
django.setup()

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import transaction
from core.models import Zayavki, ZayavkaFile, Polzovateli
from core.permissions import IsAdminOnly

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/atc_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ATCAudioImporter:
    def __init__(self, audio_dir, system_user_login='admin'):
        """
        Инициализация импортера
        
        Args:
            audio_dir (str): Путь к папке с аудиозаписями АТС
            system_user_login (str): Логин системного пользователя для прикрепления файлов
        """
        self.audio_dir = Path(audio_dir)
        self.system_user = self._get_system_user(system_user_login)
        self.processed_files = set()
        self.load_processed_files()
        
    def _get_system_user(self, login):
        """Получение системного пользователя"""
        try:
            return Polzovateli.objects.get(login=login)
        except Polzovateli.DoesNotExist:
            logger.error(f"Системный пользователь {login} не найден")
            sys.exit(1)
    
    def load_processed_files(self):
        """Загрузка списка уже обработанных файлов"""
        processed_file = Path('logs/processed_audio_files.txt')
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                self.processed_files = set(line.strip() for line in f)
    
    def save_processed_files(self):
        """Сохранение списка обработанных файлов"""
        processed_file = Path('logs/processed_audio_files.txt')
        processed_file.parent.mkdir(exist_ok=True)
        with open(processed_file, 'w') as f:
            for filename in self.processed_files:
                f.write(f"{filename}\n")
    
    def extract_phone_from_filename(self, filename):
        """
        Извлечение номера телефона из имени файла
        Поддерживает различные форматы имен файлов АТС
        """
        # Убираем расширение
        name = Path(filename).stem
        
        # Паттерны для поиска номеров телефонов
        patterns = [
            r'(\+?[78]?\d{10,11})',  # +7XXXXXXXXXX или 8XXXXXXXXXX
            r'(\d{10,11})',          # XXXXXXXXXX
            r'(\+?\d{10,15})',       # Любой номер с + или без
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name)
            if match:
                phone = match.group(1)
                # Нормализация номера
                if phone.startswith('8') and len(phone) == 11:
                    phone = '+7' + phone[1:]
                elif phone.startswith('7') and len(phone) == 11:
                    phone = '+' + phone
                elif len(phone) == 10:
                    phone = '+7' + phone
                return phone
        
        return None
    
    def find_zayavka_by_phone(self, phone):
        """
        Поиск заявки по номеру телефона
        Ищет в phone_client и phone_atc
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
    
    def is_audio_file(self, file_path):
        """Проверка, является ли файл аудио"""
        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'}
        return file_path.suffix.lower() in audio_extensions
    
    def should_process_file(self, file_path):
        """Проверка, нужно ли обрабатывать файл"""
        # Проверяем, не обработан ли уже файл
        if str(file_path) in self.processed_files:
            return False
        
        # Проверяем, что это аудиофайл
        if not self.is_audio_file(file_path):
            return False
        
        # Проверяем размер файла (не менее 1KB)
        if file_path.stat().st_size < 1024:
            logger.warning(f"Файл слишком маленький: {file_path}")
            return False
        
        return True
    
    def attach_audio_to_zayavka(self, file_path, zayavka):
        """Прикрепление аудиофайла к заявке"""
        try:
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
    
    def process_audio_files(self, dry_run=False):
        """Обработка всех аудиофайлов в папке"""
        if not self.audio_dir.exists():
            logger.error(f"Папка с аудиозаписями не найдена: {self.audio_dir}")
            return
        
        logger.info(f"Начинаем обработку папки: {self.audio_dir}")
        
        processed_count = 0
        attached_count = 0
        error_count = 0
        
        # Рекурсивно обходим все файлы
        for file_path in self.audio_dir.rglob('*'):
            if not file_path.is_file():
                continue
            
            if not self.should_process_file(file_path):
                continue
            
            processed_count += 1
            
            try:
                # Извлекаем номер телефона из имени файла
                phone = self.extract_phone_from_filename(file_path.name)
                
                if not phone:
                    logger.warning(f"Не удалось извлечь номер телефона из: {file_path.name}")
                    error_count += 1
                    continue
                
                # Ищем заявку
                zayavka = self.find_zayavka_by_phone(phone)
                
                if not zayavka:
                    logger.warning(f"Заявка не найдена для номера {phone} (файл: {file_path.name})")
                    error_count += 1
                    continue
                
                if dry_run:
                    logger.info(f"[DRY RUN] Найдена заявка {zayavka.id} для {phone} - {file_path.name}")
                    attached_count += 1
                else:
                    # Прикрепляем аудио к заявке
                    if self.attach_audio_to_zayavka(file_path, zayavka):
                        attached_count += 1
                        # Добавляем в список обработанных
                        self.processed_files.add(str(file_path))
                    else:
                        error_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка обработки файла {file_path}: {e}")
                error_count += 1
        
        # Сохраняем список обработанных файлов
        if not dry_run:
            self.save_processed_files()
        
        logger.info(f"Обработка завершена:")
        logger.info(f"  Обработано файлов: {processed_count}")
        logger.info(f"  Прикреплено к заявкам: {attached_count}")
        logger.info(f"  Ошибок: {error_count}")
    
    def cleanup_old_files(self, days=30):
        """Очистка старых обработанных файлов из списка"""
        cutoff_date = datetime.now() - timedelta(days=days)
        processed_file = Path('logs/processed_audio_files.txt')
        
        if not processed_file.exists():
            return
        
        cleaned_files = []
        with open(processed_file, 'r') as f:
            for line in f:
                file_path = Path(line.strip())
                if file_path.exists():
                    # Проверяем дату модификации файла
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime > cutoff_date:
                        cleaned_files.append(line)
        
        with open(processed_file, 'w') as f:
            f.writelines(cleaned_files)
        
        logger.info(f"Очищено {len(self.processed_files) - len(cleaned_files)} старых записей")

def main():
    parser = argparse.ArgumentParser(description='Импорт аудиозаписей из АТС в CRM')
    parser.add_argument('audio_dir', help='Путь к папке с аудиозаписями АТС')
    parser.add_argument('--system-user', default='admin', help='Логин системного пользователя')
    parser.add_argument('--dry-run', action='store_true', help='Только показать, что будет сделано')
    parser.add_argument('--cleanup', action='store_true', help='Очистить старые записи')
    parser.add_argument('--cleanup-days', type=int, default=30, help='Количество дней для очистки')
    
    args = parser.parse_args()
    
    # Создаем папку для логов
    Path('logs').mkdir(exist_ok=True)
    
    importer = ATCAudioImporter(args.audio_dir, args.system_user)
    
    if args.cleanup:
        importer.cleanup_old_files(args.cleanup_days)
        return
    
    importer.process_audio_files(dry_run=args.dry_run)

if __name__ == '__main__':
    main() 