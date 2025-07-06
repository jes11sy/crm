"""
Тесты бизнес-логики системы
"""

from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from core.models import Gorod, RK, TipZayavki, Master, Zayavki, MasterPayout


class BusinessLogicTest(TestCase):
    """Тесты бизнес-логики"""
    
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
    
    def test_zayavka_calculation_and_payout_creation(self):
        """Тест расчета заявки и создания выплаты"""
        # Создаем заявку с расчетами
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234569',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент',
            address='ул. Тестовая, 1',
            meeting_date=timezone.now(),
            tip_techniki='Холодильник',
            problema='Не работает',
            kc_name='КЦ-1',
            itog=Decimal('1000.00'),
            rashod=Decimal('200.00'),
            master=self.master
        )
        
        # Проверяем автоматический расчет
        self.assertEqual(zayavka.chistymi, Decimal('800.00'))
        self.assertEqual(zayavka.sdacha_mastera, Decimal('800.00'))
        
        # Меняем статус на завершающий
        zayavka.status = 'Готово'
        zayavka.save()
        
        # Проверяем, что создалась выплата
        payout = MasterPayout.objects.filter(zayavka=zayavka).first()
        self.assertIsNotNone(payout)
        self.assertEqual(payout.summa, Decimal('800.00'))
        self.assertEqual(payout.status, 'pending')
    
    def test_zayavka_calculation_without_master(self):
        """Тест расчета заявки без мастера (выплата не должна создаваться)"""
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234569',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент',
            address='ул. Тестовая, 1',
            meeting_date=timezone.now(),
            tip_techniki='Холодильник',
            problema='Не работает',
            kc_name='КЦ-1',
            itog=Decimal('1000.00'),
            rashod=Decimal('200.00')
            # Без мастера
        )
        
        # Проверяем расчет
        self.assertEqual(zayavka.chistymi, Decimal('800.00'))
        self.assertEqual(zayavka.sdacha_mastera, Decimal('800.00'))
        
        # Меняем статус на завершающий
        zayavka.status = 'Готово'
        zayavka.save()
        
        # Проверяем, что выплата НЕ создалась
        payout = MasterPayout.objects.filter(zayavka=zayavka).first()
        self.assertIsNone(payout)
    
    def test_zayavka_calculation_negative_chistymi(self):
        """Тест расчета заявки с отрицательными чистыми (сдача мастера должна быть 0)"""
        zayavka = Zayavki.objects.create(
            rk=self.rk,
            gorod=self.gorod,
            phone_client='+79001234569',
            tip_zayavki=self.tip_zayavki,
            client_name='Клиент',
            address='ул. Тестовая, 1',
            meeting_date=timezone.now(),
            tip_techniki='Холодильник',
            problema='Не работает',
            kc_name='КЦ-1',
            itog=Decimal('100.00'),
            rashod=Decimal('200.00'),
            master=self.master
        )
        
        # Проверяем расчет
        self.assertEqual(zayavka.chistymi, Decimal('-100.00'))
        self.assertIsNone(zayavka.sdacha_mastera)  # Должно быть None для отрицательных значений
        
        # Меняем статус на завершающий
        zayavka.status = 'Готово'
        zayavka.save()
        
        # Проверяем, что выплата НЕ создалась (отрицательные чистые)
        payout = MasterPayout.objects.filter(zayavka=zayavka).first()
        self.assertIsNone(payout) 