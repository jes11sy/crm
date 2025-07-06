from django.test import TestCase
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from datetime import date
import uuid

from core.models import (
    Gorod, TipZayavki, RK, Master, TipTranzakcii, Tranzakcii,
    Roli, Polzovateli, PhoneGoroda, Zayavki, ZayavkaFile, MasterPayout
)
from core.serializers import (
    GorodSerializer, TipZayavkiSerializer, RKSerializer, MasterSerializer,
    TipTranzakciiSerializer, TranzakciiSerializer, RoliSerializer,
    PolzovateliSerializer, PhoneGorodaSerializer, ZayavkiSerializer,
    ZayavkaFileSerializer, MasterPayoutSerializer
)


class GorodSerializerTest(TestCase):
    """Тесты для GorodSerializer"""
    
    def setUp(self):
        self.gorod_data = {'name': 'Москва'}
        self.gorod = Gorod.objects.create(name='Москва')
    
    def test_gorod_serializer_valid_data(self):
        """Тест валидных данных"""
        unique_data = {'name': 'Санкт-Петербург'}
        serializer = GorodSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_gorod_serializer_invalid_data(self):
        """Тест невалидных данных"""
        invalid_data = {'name': ''}
        serializer = GorodSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
    
    def test_gorod_serializer_create(self):
        """Тест создания объекта"""
        unique_data = {'name': 'Санкт-Петербург'}
        serializer = GorodSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        gorod = serializer.save()
        self.assertEqual(gorod.name, 'Санкт-Петербург')
    
    def test_gorod_serializer_update(self):
        """Тест обновления объекта"""
        serializer = GorodSerializer(self.gorod, data={'name': 'Санкт-Петербург'})
        self.assertTrue(serializer.is_valid())
        gorod = serializer.save()
        self.assertEqual(gorod.name, 'Санкт-Петербург')


class TipZayavkiSerializerTest(TestCase):
    """Тесты для TipZayavkiSerializer"""
    
    def setUp(self):
        self.tip_data = {'name': 'Ремонт холодильника'}
        self.tip = TipZayavki.objects.create(name='Ремонт холодильника')
    
    def test_tip_zayavki_serializer_valid_data(self):
        """Тест валидных данных"""
        unique_data = {'name': 'Ремонт стиральной машины'}
        serializer = TipZayavkiSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_tip_zayavki_serializer_create(self):
        """Тест создания объекта"""
        unique_data = {'name': 'Ремонт стиральной машины'}
        serializer = TipZayavkiSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        tip = serializer.save()
        self.assertEqual(tip.name, 'Ремонт стиральной машины')


class RKSerializerTest(TestCase):
    """Тесты для RKSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.rk_data = {
            'rk_name': 'РК Москва',
            'gorod': self.gorod.id,
            'phone': '+79001234567'
        }
        self.rk = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod,
            phone='+79001234567'
        )
    
    def test_rk_serializer_valid_data(self):
        """Тест валидных данных"""
        unique_data = {
            'rk_name': 'РК Санкт-Петербург',
            'gorod': self.gorod.id,
            'phone': '+79001234568'
        }
        serializer = RKSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_rk_serializer_create(self):
        """Тест создания объекта"""
        unique_data = {
            'rk_name': 'РК Санкт-Петербург',
            'gorod': self.gorod.id,
            'phone': '+79001234568'
        }
        serializer = RKSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        rk = serializer.save()
        self.assertEqual(rk.rk_name, 'РК Санкт-Петербург')
        self.assertEqual(rk.gorod, self.gorod)


class MasterSerializerTest(TestCase):
    """Тесты для MasterSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        unique = str(uuid.uuid4())[:8]
        self.master_data = {
            'name': 'Иван Иванов',
            'login': f'ivan_{unique}',
            'password': 'testpass123',
            'gorod': self.gorod.id,
            'phone': '+79001234567',
            'birth_date': '1990-01-01',
            'is_active': True
        }
        self.master = Master.objects.create(
            name='Иван Иванов',
            login=f'ivan_{unique}',
            password='testpass123',
            gorod=self.gorod,
            phone='+79001234567',
            birth_date=date(1990, 1, 1),
            is_active=True
        )
    
    def test_master_serializer_valid_data(self):
        """Тест валидных данных"""
        unique = str(uuid.uuid4())[:8]
        unique_data = {
            'name': 'Петр Петров',
            'login': f'petr_{unique}',
            'password': 'testpass123',
            'gorod': self.gorod.id,
            'phone': '+79001234568',
            'birth_date': '1990-01-01',
            'is_active': True
        }
        serializer = MasterSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_master_serializer_create(self):
        """Тест создания объекта"""
        unique = str(uuid.uuid4())[:8]
        unique_data = {
            'name': 'Петр Петров',
            'login': f'petr_{unique}',
            'password': 'testpass123',
            'gorod': self.gorod.id,
            'phone': '+79001234568',
            'birth_date': '1990-01-01',
            'is_active': True
        }
        serializer = MasterSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        master = serializer.save()
        self.assertEqual(master.name, 'Петр Петров')
        self.assertEqual(master.gorod, self.gorod)
    
    def test_master_serializer_password_hashing(self):
        """Тест хеширования пароля"""
        unique = str(uuid.uuid4())[:8]
        unique_data = {
            'name': 'Сидор Сидоров',
            'login': f'sidor_{unique}',
            'password': 'testpass123',
            'gorod': self.gorod.id,
            'phone': '+79001234569',
            'birth_date': '1990-01-01',
            'is_active': True
        }
        serializer = MasterSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        master = serializer.save()
        self.assertNotEqual(master.password, 'testpass123')
        # Проверяем, что пароль хеширован (начинается с pbkdf2_sha256$)
        self.assertTrue(master.password.startswith('pbkdf2_sha256$'))


class TipTranzakciiSerializerTest(TestCase):
    """Тесты для TipTranzakciiSerializer"""
    
    def setUp(self):
        self.tip_data = {'name': 'Выплата мастеру'}
        self.tip = TipTranzakcii.objects.create(name='Выплата мастеру')
    
    def test_tip_tranzakcii_serializer_valid_data(self):
        """Тест валидных данных"""
        unique_data = {'name': 'Расход'}
        serializer = TipTranzakciiSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_tip_tranzakcii_serializer_create(self):
        """Тест создания объекта"""
        unique_data = {'name': 'Расход'}
        serializer = TipTranzakciiSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        tip = serializer.save()
        self.assertEqual(tip.name, 'Расход')


class TranzakciiSerializerTest(TestCase):
    """Тесты для TranzakciiSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.tip = TipTranzakcii.objects.create(name='Выплата мастеру')
        self.tranzakciya_data = {
            'gorod': self.gorod.id,
            'tip_tranzakcii': self.tip.id,
            'summa': '1000.00',
            'note': 'Тестовая транзакция',
            'date': '2025-07-06'
        }
        self.tranzakciya = Tranzakcii.objects.create(
            gorod=self.gorod,
            tip_tranzakcii=self.tip,
            summa=Decimal('1000.00'),
            note='Тестовая транзакция'
        )
    
    def test_tranzakcii_serializer_valid_data(self):
        """Тест валидных данных"""
        serializer = TranzakciiSerializer(data=self.tranzakciya_data)
        self.assertTrue(serializer.is_valid())
    
    def test_tranzakcii_serializer_create(self):
        """Тест создания объекта"""
        serializer = TranzakciiSerializer(data=self.tranzakciya_data)
        self.assertTrue(serializer.is_valid())
        tranzakciya = serializer.save()
        self.assertEqual(tranzakciya.gorod, self.gorod)
        self.assertEqual(tranzakciya.summa, Decimal('1000.00'))


class RoliSerializerTest(TestCase):
    """Тесты для RoliSerializer"""
    
    def setUp(self):
        self.rol_data = {'name': 'admin'}
        self.rol = Roli.objects.create(name='admin')
    
    def test_roli_serializer_valid_data(self):
        """Тест валидных данных"""
        unique_data = {'name': 'manager'}
        serializer = RoliSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_roli_serializer_create(self):
        """Тест создания объекта"""
        unique_data = {'name': 'manager'}
        serializer = RoliSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        rol = serializer.save()
        self.assertEqual(rol.name, 'manager')


class PolzovateliSerializerTest(TestCase):
    """Тесты для PolzovateliSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
        unique = str(uuid.uuid4())[:8]
        self.user_data = {
            'name': 'Админ Админов',
            'login': f'admin_{unique}',
            'password': 'adminpass123',
            'gorod': self.gorod.id,
            'rol': self.rol.id,
            'is_active': True
        }
        self.user = Polzovateli.objects.create(
            name='Админ Админов',
            login=f'admin_{unique}',
            password='adminpass123',
            gorod=self.gorod,
            rol=self.rol,
            is_active=True
        )
    
    def test_polzovateli_serializer_valid_data(self):
        """Тест валидных данных"""
        unique = str(uuid.uuid4())[:8]
        unique_data = {
            'name': 'Менеджер Менеджеров',
            'login': f'manager_{unique}',
            'password': 'managerpass123',
            'gorod': self.gorod.id,
            'rol': self.rol.id,
            'is_active': True
        }
        serializer = PolzovateliSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_polzovateli_serializer_create(self):
        """Тест создания объекта"""
        unique = str(uuid.uuid4())[:8]
        unique_data = {
            'name': 'Менеджер Менеджеров',
            'login': f'manager_{unique}',
            'password': 'managerpass123',
            'gorod': self.gorod.id,
            'rol': self.rol.id,
            'is_active': True
        }
        serializer = PolzovateliSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.name, 'Менеджер Менеджеров')
        self.assertEqual(user.gorod, self.gorod)


class PhoneGorodaSerializerTest(TestCase):
    """Тесты для PhoneGorodaSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.phone_data = {
            'gorod': self.gorod.id,
            'phone': '+79001234567'
        }
        self.phone = PhoneGoroda.objects.create(
            gorod=self.gorod,
            phone='+79001234567'
        )
    
    def test_phone_goroda_serializer_valid_data(self):
        """Тест валидных данных"""
        unique_data = {
            'gorod': self.gorod.id,
            'phone': '+79001234568'
        }
        serializer = PhoneGorodaSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_phone_goroda_serializer_create(self):
        """Тест создания объекта"""
        unique_data = {
            'gorod': self.gorod.id,
            'phone': '+79001234568'
        }
        serializer = PhoneGorodaSerializer(data=unique_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        phone = serializer.save()
        self.assertEqual(phone.gorod, self.gorod)
        self.assertEqual(phone.phone, '+79001234568')


class ZayavkiSerializerTest(TestCase):
    """Тесты для ZayavkiSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.master = Master.objects.create(
            name='Иван Иванов',
            login='ivan',
            password='testpass123',
            gorod=self.gorod
        )
        self.rk = RK.objects.create(
            rk_name='РК Москва',
            gorod=self.gorod,
            phone='+79001234567'
        )
        self.tip_zayavki = TipZayavki.objects.create(name='Ремонт холодильника')
        
        self.zayavka_data = {
            'gorod': self.gorod.id,
            'master': self.master.id,
            'rk': self.rk.id,
            'tip_zayavki': self.tip_zayavki.id,
            'phone_client': '+79001234567',
            'client_name': 'Клиент Клиентов',
            'address': 'ул. Пушкина, 1',
            'tip_techniki': 'Холодильник',
            'problema': 'Не морозит',
            'kc_name': 'КЦ Москва',
            'status': 'Ожидает',
            'meeting_date': '2024-01-15'
        }
        self.zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            master=self.master,
            rk=self.rk,
            tip_zayavki=self.tip_zayavki,
            phone_client='+79001234567',
            client_name='Клиент Клиентов',
            address='ул. Пушкина, 1',
            tip_techniki='Холодильник',
            problema='Не морозит',
            kc_name='КЦ Москва',
            status='Ожидает',
            meeting_date='2024-01-15'
        )
    
    def test_zayavki_serializer_valid_data(self):
        """Тест валидных данных"""
        serializer = ZayavkiSerializer(data=self.zayavka_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_zayavki_serializer_create(self):
        """Тест создания объекта"""
        serializer = ZayavkiSerializer(data=self.zayavka_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        zayavka = serializer.save()
        self.assertEqual(zayavka.client_name, 'Клиент Клиентов')
        self.assertEqual(zayavka.gorod, self.gorod)
        self.assertEqual(zayavka.master, self.master)


class ZayavkaFileSerializerTest(TestCase):
    """Тесты для ZayavkaFileSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            phone_client='+79001234567',
            client_name='Клиент',
            status='Ожидает',
            meeting_date='2024-01-15'
        )
        self.file_data = {
            'zayavka': self.zayavka.id,
            'type': 'audio'
        }
        self.file = ZayavkaFile.objects.create(
            zayavka=self.zayavka,
            file='test.mp3',
            type='audio'
        )
    
    def test_zayavka_file_serializer_valid_data(self):
        """Тест валидных данных"""
        serializer = ZayavkaFileSerializer(data=self.file_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
    
    def test_zayavka_file_serializer_create(self):
        """Тест создания объекта"""
        serializer = ZayavkaFileSerializer(data=self.file_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        file_obj = serializer.save()
        self.assertEqual(file_obj.zayavka, self.zayavka)
        self.assertEqual(file_obj.type, 'audio')


class MasterPayoutSerializerTest(TestCase):
    """Тесты для MasterPayoutSerializer"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name='Москва')
        self.master = Master.objects.create(
            name='Иван Иванов',
            login='ivan',
            password='testpass123',
            gorod=self.gorod
        )
        self.zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            master=self.master,
            phone_client='+79001234567',
            client_name='Клиент',
            status='Завершена',
            meeting_date='2024-01-15'
        )
        self.payout_data = {
            'zayavka': self.zayavka.id,
            'summa': '500.00',
            'status': 'pending',
            'comment': 'Тестовая выплата'
        }
        self.payout = MasterPayout.objects.create(
            zayavka=self.zayavka,
            summa=Decimal('500.00'),
            status='pending',
            comment='Тестовая выплата'
        )
    
    def test_master_payout_serializer_valid_data(self):
        """Тест валидных данных"""
        serializer = MasterPayoutSerializer(data=self.payout_data)
        self.assertTrue(serializer.is_valid())
    
    def test_master_payout_serializer_create(self):
        """Тест создания объекта"""
        # Создаем новую заявку для теста
        new_zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            master=self.master,
            phone_client='+79001234567',
            client_name='Клиент2',
            status='Завершена',
            meeting_date='2024-01-16'
        )
        payout_data = {
            'zayavka': new_zayavka.id,
            'summa': '500.00',
            'status': 'pending',
            'comment': 'Тестовая выплата'
        }
        serializer = MasterPayoutSerializer(data=payout_data)
        if not serializer.is_valid():
            print(f"Ошибки валидации: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        payout = serializer.save()
        self.assertEqual(payout.zayavka, new_zayavka)
        self.assertEqual(payout.summa, Decimal('500.00'))
        self.assertEqual(payout.status, 'pending') 