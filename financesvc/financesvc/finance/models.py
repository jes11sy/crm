from django.db import models

# Create your models here.

class TipTranzakcii(models.Model):
    """Тип транзакции"""
    name = models.CharField('Тип транзакции', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Тип транзакции'
        verbose_name_plural = 'Типы транзакций'
        ordering = ['name']

    def __str__(self):
        return self.name

class Tranzakciya(models.Model):
    """Транзакция"""
    tip = models.ForeignKey(TipTranzakcii, on_delete=models.PROTECT, verbose_name='Тип транзакции')
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    description = models.TextField('Описание')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    status = models.CharField('Статус', max_length=50, default='pending')
    # user_id, master_id — для интеграции с User Service и Master Service
    user_id = models.IntegerField('ID пользователя')
    master_id = models.IntegerField('ID мастера', null=True, blank=True)
    zayavka_id = models.IntegerField('ID заявки', null=True, blank=True)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tip.name} - {self.amount} ({self.status})"

class Payout(models.Model):
    """Выплата"""
    master_id = models.IntegerField('ID мастера')
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    description = models.TextField('Описание')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    status = models.CharField('Статус', max_length=50, default='pending')
    payment_method = models.CharField('Способ выплаты', max_length=50, default='bank')

    class Meta:
        verbose_name = 'Выплата'
        verbose_name_plural = 'Выплаты'
        ordering = ['-created_at']

    def __str__(self):
        return f"Выплата {self.master_id} - {self.amount} ({self.status})"
