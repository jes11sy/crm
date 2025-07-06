"""
Финансовые модели системы
"""

from django.db import models
from decimal import Decimal


class TipTranzakcii(models.Model):
    """Модель типа транзакции"""
    name = models.CharField('Название транзакции', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Тип транзакции'
        verbose_name_plural = 'Типы транзакций'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tranzakcii(models.Model):
    """Модель транзакции"""
    gorod = models.ForeignKey('Gorod', on_delete=models.CASCADE, verbose_name='Город')
    tip_tranzakcii = models.ForeignKey(TipTranzakcii, on_delete=models.CASCADE, verbose_name='Тип транзакции')
    summa = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    note = models.TextField('Примечание', blank=True, null=True)
    date = models.DateField('Дата', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['gorod', 'date']),
            models.Index(fields=['tip_tranzakcii']),
        ]
    
    def __str__(self):
        return f"{self.tip_tranzakcii} - {self.summa} ({self.gorod})"


class MasterPayout(models.Model):
    """Модель выплаты мастеру"""
    PAYOUT_STATUS = [
        ('pending', 'Ожидает перевод'),
        ('checking', 'Отправлено на проверку'),
        ('confirmed', 'Подтверждено'),
    ]
    zayavka = models.OneToOneField('Zayavki', on_delete=models.CASCADE, related_name='payout', verbose_name='Заявка')
    summa = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    status = models.CharField('Статус выплаты', max_length=20, choices=PAYOUT_STATUS, default='pending')
    comment = models.TextField('Комментарий руководителя', blank=True, null=True)
    file = models.FileField('Чек перевода', upload_to='payout_cheques/', blank=True, null=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Выплата мастеру'
        verbose_name_plural = 'Выплаты мастерам'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'Выплата по заявке {self.zayavka.id} - {self.summa}' 