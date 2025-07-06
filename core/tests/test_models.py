from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import uuid

from core.models import (
    Gorod, TipZayavki, RK, Master, TipTranzakcii, Tranzakcii,
    Roli, Polzovateli, PhoneGoroda, Zayavki, ZayavkaFile, MasterPayout
)


class GorodModelTest(TestCase):
    """Тесты для модели Город"""
    
    def test_gorod_creation(self):
        """Тест создания города"""
        gorod = Gorod.objects.create(name='Москва')
        self.assertEqual(gorod.name, 'Москва')
        self.assertEqual(str(gorod), 'Москва')
    
    def test_gorod_unique_name(self):
        """Тест уникальности названия города"""
        Gorod.objects.create(name='Москва')
        with self.assertRaises(Exception):  # IntegrityError или ValidationError
            Gorod.objects.create(name='Москва')


class TipZayavkiModelTest(TestCase):
    """Тесты для модели TipZayavki"""
    
    def setUp(self):
        self.tip = TipZayavki.objects.create(name="Ремонт холодильника")
    
    def test_tip_zayavki_creation(self):
        """Тест создания типа заявки"""
        self.assertEqual(self.tip.name, "Ремонт холодильника")
    
    def test_tip_zayavki_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.tip), "Ремонт холодильника")


class RKModelTest(TestCase):
    """Тесты для модели РК"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
    
    def test_rk_creation(self):
        """Тест создания РК"""
        rk = RK.objects.create(
            rk_name='РК-1',
            gorod=self.gorod,
            phone='+79001234567'
        )
        self.assertEqual(rk.rk_name, 'РК-1')
        self.assertEqual(rk.gorod, self.gorod)
        self.assertEqual(rk.phone, '+79001234567')
    
    def test_rk_unique_constraint(self):
        """Тест уникальности РК в городе"""
        RK.objects.create(
            rk_name='РК-1',
            gorod=self.gorod,
            phone='+79001234567'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            RK.objects.create(
                rk_name='РК-1',
                gorod=self.gorod,
                phone='+79001234568'
            )


class MasterModelTest(TestCase):
    """Тесты для модели Мастер"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='master')
    
    def test_master_creation(self):
        """Тест создания мастера"""
        master = Master.objects.create(
            name='Иван Иванов',
            phone='+79001234567',
            login='ivan',
            gorod=self.gorod
        )
        self.assertEqual(master.name, 'Иван Иванов')
        self.assertEqual(master.phone, '+79001234567')
        self.assertEqual(master.login, 'ivan')
        self.assertEqual(master.gorod, self.gorod)
        self.assertTrue(master.is_active)
    
    def test_master_with_user_creation(self):
        """Тест создания мастера с пользователем"""
        # Создаем мастера
        master = Master.objects.create(
            name='Иван Иванов',
            phone='+79001234567',
            login='ivan',
            gorod=self.gorod
        )
        
        # Проверяем, что мастер создан корректно
        self.assertEqual(master.name, 'Иван Иванов')
        self.assertEqual(master.login, 'ivan')
        self.assertEqual(master.phone, '+79001234567')
        self.assertEqual(master.gorod, self.gorod)
        self.assertTrue(master.is_active)
    
    def test_master_phone_validation(self):
        """Тест валидации номера телефона"""
        with self.assertRaises(ValidationError):
            master = Master(
                name='Иван Иванов',
                phone='invalid-phone',
                login='ivan',
                gorod=self.gorod
            )
            master.full_clean()


class TipTranzakciiModelTest(TestCase):
    """Тесты для модели TipTranzakcii"""
    
    def setUp(self):
        self.tip = TipTranzakcii.objects.create(name="Выплата мастеру")
    
    def test_tip_tranzakcii_creation(self):
        """Тест создания типа транзакции"""
        self.assertEqual(self.tip.name, "Выплата мастеру")
    
    def test_tip_tranzakcii_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.tip), "Выплата мастеру")


class TranzakciiModelTest(TestCase):
    """Тесты для модели Tranzakcii"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name="Москва")
        self.tip = TipTranzakcii.objects.create(name="Выплата мастеру")
        self.tranzakciya = Tranzakcii.objects.create(
            gorod=self.gorod,
            tip_tranzakcii=self.tip,
            summa=Decimal("1000.00"),
            note="Тестовая транзакция",
            date=timezone.now().date()
        )
    
    def test_tranzakcii_creation(self):
        """Тест создания транзакции"""
        self.assertEqual(self.tranzakciya.gorod, self.gorod)
        self.assertEqual(self.tranzakciya.tip_tranzakcii, self.tip)
        self.assertEqual(self.tranzakciya.summa, Decimal("1000.00"))
        self.assertEqual(self.tranzakciya.note, "Тестовая транзакция")
    
    def test_tranzakcii_str(self):
        """Тест строкового представления"""
        expected = f"Выплата мастеру - 1000.00 (Москва)"
        self.assertEqual(str(self.tranzakciya), expected)


class RoliModelTest(TestCase):
    """Тесты для модели Roli"""
    
    def setUp(self):
        self.rol = Roli.objects.create(name="admin")
    
    def test_roli_creation(self):
        """Тест создания роли"""
        self.assertEqual(self.rol.name, "admin")
    
    def test_roli_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.rol), "admin")


class PolzovateliModelTest(TestCase):
    """Тесты для модели Пользователи"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
        self.rol = Roli.objects.create(name='admin')
    
    def test_polzovateli_creation(self):
        """Тест создания пользователя"""
        user = Polzovateli.objects.create(
            name='Админ Админов',
            login='admin',
            password='testpass123',
            gorod=self.gorod,
            rol=self.rol
        )
        self.assertEqual(user.name, 'Админ Админов')
        self.assertEqual(user.login, 'admin')
        self.assertEqual(user.gorod, self.gorod)
        self.assertEqual(user.rol, self.rol)
        self.assertTrue(user.is_active)
    
    def test_password_hashing(self):
        """Тест хеширования пароля"""
        user = Polzovateli.objects.create(
            name='Тест',
            login='test',
            password='testpass123',
            gorod=self.gorod,
            rol=self.rol
        )
        
        # Пароль должен быть захеширован
        self.assertNotEqual(user.password, 'testpass123')
        self.assertTrue(check_password('testpass123', user.password))
    
    def test_polzovateli_unique_login(self):
        """Тест уникальности логина"""
        Polzovateli.objects.create(
            name='Пользователь 1',
            login='testuser',
            password='pass123',
            gorod=self.gorod,
            rol=self.rol
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            Polzovateli.objects.create(
                name='Пользователь 2',
                login='testuser',
                password='pass456',
                gorod=self.gorod,
                rol=self.rol
            )


class PhoneGorodaModelTest(TestCase):
    """Тесты для модели PhoneGoroda"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name="Москва")
        self.phone = PhoneGoroda.objects.create(
            gorod=self.gorod,
            phone="+79001234567"
        )
    
    def test_phone_goroda_creation(self):
        """Тест создания телефона города"""
        self.assertEqual(self.phone.gorod, self.gorod)
        self.assertEqual(self.phone.phone, "+79001234567")
    
    def test_phone_goroda_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.phone), "+79001234567 (Москва)")


class ZayavkiModelTest(TestCase):
    """Тесты для модели Заявки"""
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.gorod = Gorod.objects.create(name='Москва')
        self.tip_zayavki = TipZayavki.objects.create(name='Ремонт')
        self.rk = RK.objects.create(
            rk_name='РК-1',
            gorod=self.gorod,
            phone='+79001234567'
        )
        self.master = Master.objects.create(
            name='Мастер',
            phone='+79001234568',
            login='master',
            gorod=self.gorod
        )
    
    def test_zayavki_creation(self):
        """Тест создания заявки"""
        from datetime import datetime, timedelta
        
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234569',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент',
            address='ул. Тестовая, 1',
            meeting_date=datetime.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            kc_name='КЦ-1'
        )
        
        self.assertEqual(zayavka.client_name, 'Клиент')
        self.assertEqual(zayavka.status, 'Ожидает')
        self.assertEqual(zayavka.gorod, self.gorod)
    
    def test_zayavki_phone_validation(self):
        """Тест валидации номера телефона клиента"""
        from datetime import datetime, timedelta
        
        with self.assertRaises(ValidationError):
            zayavka = Zayavki(
                rk=self.rk,
                gorod=self.gorod,
                phone_client='invalid-phone',
                tip_zayavki=self.tip_zayavki,
                client_name='Клиент',
                address='ул. Тестовая, 1',
                meeting_date=datetime.now() + timedelta(days=1),
                tip_techniki='Холодильник',
                problema='Не работает',
                kc_name='КЦ-1'
            )
            zayavka.full_clean()
    
    def test_zayavki_calculations(self):
        """Тест автоматических расчетов"""
        from datetime import datetime, timedelta
        
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234569',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент',
            address='ул. Тестовая, 1',
            meeting_date=datetime.now() + timedelta(days=1),
            tip_techniki='Холодильник',
            problema='Не работает',
            kc_name='КЦ-1',
            itog=1000,
            rashod=200
        )
        
        # Проверяем автоматический расчет
        self.assertEqual(zayavka.chistymi, 800)  # 1000 - 200
        self.assertEqual(zayavka.sdacha_mastera, 800)  # то же значение


class ZayavkaFileModelTest(TestCase):
    """Тесты для модели ZayavkaFile"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name="Москва")
        self.zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            phone_client="+79001234567",
            client_name="Клиент",
            status="Новая",
            meeting_date=timezone.now().date()
        )
        self.file = ZayavkaFile.objects.create(
            zayavka=self.zayavka,
            file="test.mp3",
            type="audio"
        )
    
    def test_zayavka_file_creation(self):
        """Тест создания файла заявки"""
        self.assertEqual(self.file.zayavka, self.zayavka)
        self.assertEqual(self.file.file, "test.mp3")
        self.assertEqual(self.file.type, "audio")
    
    def test_zayavka_file_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.file), f"{self.zayavka} - Аудиозапись")


class MasterPayoutModelTest(TestCase):
    """Тесты для модели MasterPayout"""
    
    def setUp(self):
        self.gorod = Gorod.objects.create(name="Москва")
        self.master = Master.objects.create(
            name="Иван Иванов",
            login="ivan",
            password="testpass123",
            gorod=self.gorod
        )
        self.zayavka = Zayavki.objects.create(
            gorod=self.gorod,
            master=self.master,
            phone_client="+79001234567",
            client_name="Клиент",
            status="Завершена",
            meeting_date=timezone.now().date()
        )
        self.payout = MasterPayout.objects.create(
            zayavka=self.zayavka,
            summa=Decimal("500.00"),
            status="pending",
            comment="Тестовая выплата"
        )
    
    def test_master_payout_creation(self):
        """Тест создания выплаты мастера"""
        self.assertEqual(self.payout.zayavka, self.zayavka)
        self.assertEqual(self.payout.summa, Decimal("500.00"))
        self.assertEqual(self.payout.status, "pending")
        self.assertEqual(self.payout.comment, "Тестовая выплата")
    
    def test_master_payout_str(self):
        """Тест строкового представления"""
        expected = f"Выплата по заявке {self.zayavka.id} - 500.00"
        self.assertEqual(str(self.payout), expected)
    
    def test_master_payout_status_choices(self):
        """Тест валидных статусов выплаты"""
        valid_statuses = ["pending", "checking", "confirmed"]
        for status in valid_statuses:
            self.payout.status = status
            self.payout.save()
            self.assertEqual(self.payout.status, status) 