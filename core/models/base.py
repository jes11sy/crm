"""
Базовые модели системы
"""

from django.db import models


class Gorod(models.Model):
    """Модель города"""
    name = models.CharField('Город', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TipZayavki(models.Model):
    """Модель типа заявки"""
    name = models.CharField('Тип заявки', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Тип заявки'
        verbose_name_plural = 'Типы заявок'
        ordering = ['name']
    
    def __str__(self):
        return self.name 