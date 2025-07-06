"""
Модели заявок системы
"""

from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


class Zayavki(models.Model):
    """Модель заявки"""
    STATUS_CHOICES = [
        ('Звонит', 'Звонит'),
        ('Ожидает', 'Ожидает'),
        ('Ожидает Принятия', 'Ожидает Принятия'),
        ('Принял', 'Принял'),
        ('В работе', 'В работе'),
        ('Модерн', 'Модерн'),
        ('НеЗаказ', 'НеЗаказ'),
        ('Готово', 'Готово'),
        ('Отказ', 'Отказ'),
    ]
    
    rk = models.ForeignKey('RK', on_delete=models.SET_NULL, null=True, verbose_name='РК')
    gorod = models.ForeignKey('Gorod', on_delete=models.CASCADE, verbose_name='Город')
    phone_client = models.CharField(
        'Номер телефона клиента', 
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Номер телефона должен быть в формате: +999999999'
            )
        ]
    )
    phone_atc = models.CharField(
        'Номер телефона ATC', 
        max_length=20, 
        null=True, 
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Номер телефона должен быть в формате: +999999999'
            )
        ]
    )
    tip_zayavki = models.ForeignKey('TipZayavki', on_delete=models.SET_NULL, null=True, verbose_name='Тип заявки')
    client_name = models.CharField('Имя клиента', max_length=100)
    address = models.CharField('Адрес', max_length=255)
    meeting_date = models.DateTimeField('Дата встречи')
    tip_techniki = models.CharField('Тип техники', max_length=100)
    problema = models.TextField('Проблема')
    status = models.CharField('Статус', max_length=50, choices=STATUS_CHOICES, default='Ожидает')
    master = models.ForeignKey('Master', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Мастер')
    itog = models.DecimalField('Итог', max_digits=12, decimal_places=2, null=True, blank=True)
    rashod = models.DecimalField('Расход', max_digits=12, decimal_places=2, null=True, blank=True)
    chistymi = models.DecimalField('Чистыми', max_digits=12, decimal_places=2, null=True, blank=True)
    sdacha_mastera = models.DecimalField('Сдача мастера', max_digits=12, decimal_places=2, null=True, blank=True)
    comment_master = models.TextField('Комментарий мастера', blank=True, null=True)
    kc_name = models.CharField('Имя КЦ', max_length=100)
    comment_kc = models.TextField('Комментарий КЦ', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-meeting_date']
        indexes = [
            models.Index(fields=['gorod', 'status']),
            models.Index(fields=['master']),
            models.Index(fields=['meeting_date']),
            models.Index(fields=['phone_client']),
        ]
    
    def __str__(self):
        tip_name = self.tip_zayavki.name if self.tip_zayavki else "Без типа"
        return f'{self.client_name} - {tip_name} ({self.status})'
    
    def save(self, *args, **kwargs):
        # Автоматический расчет чистыми и сдачи мастера
        if self.itog is not None and self.rashod is not None:
            self.chistymi = self.itog - self.rashod
            if self.chistymi > 0:
                self.sdacha_mastera = self.chistymi
        super().save(*args, **kwargs)


class ZayavkaFile(models.Model):
    """Модель файла заявки"""
    FILE_TYPES = [
        ('bso', 'БСО'),
        ('chek', 'Чек расхода'),
        ('audio', 'Аудиозапись'),
    ]
    zayavka = models.ForeignKey('Zayavki', on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='zayavka_files/')
    type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('Polzovateli', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Файл заявки'
        verbose_name_plural = 'Файлы заявок'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f'{self.zayavka} - {self.get_type_display()}'


# Сигнал для создания выплаты при закрытии заявки
@receiver(post_save, sender=Zayavki)
def create_master_payout_on_close(sender, instance, created, **kwargs):
    """Создает выплату мастеру при закрытии заявки"""
    # Проверяем, что это не создание новой записи и статус изменился на завершающий
    if (
        not created and 
        instance.status in ['Готово', 'Модерн'] and 
        instance.master and 
        instance.chistymi and 
        instance.chistymi > 0
    ):
        # Проверяем, не была ли уже создана выплата для этой заявки
        from .finance import MasterPayout
        payout, created_payout = MasterPayout.objects.get_or_create(
            zayavka=instance,
            defaults={
                'summa': instance.chistymi,
                'status': 'pending'
            }
        )
        # Если выплата уже существовала, обновляем сумму только если она изменилась
        if not created_payout and payout.summa != instance.chistymi:
            payout.summa = instance.chistymi
            payout.save(update_fields=['summa']) 