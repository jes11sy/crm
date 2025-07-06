"""
Бизнес-модели системы
"""

from django.db import models
from django.core.validators import RegexValidator


class RK(models.Model):
    """Модель РК (Регионального контрагента)"""
    rk_name = models.CharField('РК', max_length=100)
    gorod = models.ForeignKey('Gorod', on_delete=models.CASCADE, verbose_name='Город')
    phone = models.CharField(
        'Номер телефона', 
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Номер телефона должен быть в формате: +999999999'
            )
        ]
    )
    
    class Meta:
        verbose_name = 'РК'
        verbose_name_plural = 'РК'
        unique_together = ['rk_name', 'gorod']
        ordering = ['rk_name']
    
    def __str__(self):
        return f"{self.rk_name} ({self.gorod})"


class PhoneGoroda(models.Model):
    """Модель телефона города"""
    gorod = models.ForeignKey('Gorod', on_delete=models.CASCADE, verbose_name='Город')
    phone = models.CharField(
        'Номер телефона', 
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Номер телефона должен быть в формате: +999999999'
            )
        ]
    )
    
    class Meta:
        verbose_name = 'Телефон города'
        verbose_name_plural = 'Телефоны городов'
        unique_together = ['gorod', 'phone']
        ordering = ['gorod', 'phone']
        indexes = [
            models.Index(fields=['gorod']),
        ]
    
    def __str__(self):
        return f"{self.phone} ({self.gorod})" 