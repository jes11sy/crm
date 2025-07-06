"""
Модели пользователей для микросервиса User Service
"""

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password


class Gorod(models.Model):
    """Модель города"""
    name = models.CharField('Город', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Roli(models.Model):
    """Модель роли пользователя"""
    name = models.CharField('Название роли', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Polzovateli(models.Model):
    """Модель пользователя системы"""
    gorod = models.ForeignKey(Gorod, on_delete=models.CASCADE, verbose_name='Город')
    name = models.CharField('Имя', max_length=100)
    rol = models.ForeignKey(Roli, on_delete=models.CASCADE, verbose_name='Роль')
    is_active = models.BooleanField('Статус', default=True)
    login = models.CharField('Логин', max_length=50, unique=True)
    password = models.CharField('Пароль', max_length=100)
    note = models.TextField('Примечание', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['name']
        indexes = [
            models.Index(fields=['gorod', 'is_active']),
            models.Index(fields=['login']),
            models.Index(fields=['rol']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.login})"
    
    def save(self, *args, **kwargs):
        # Хешируем пароль при создании или изменении
        if self._state.adding:
            self.password = make_password(self.password)
        else:
            # Проверяем, изменился ли пароль
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                if old_instance.password != self.password:
                    self.password = make_password(self.password)
            except self.__class__.DoesNotExist:
                self.password = make_password(self.password)
        super().save(*args, **kwargs)

    @property
    def is_authenticated(self):
        return True


class Master(models.Model):
    """Модель мастера"""
    gorod = models.ForeignKey(Gorod, on_delete=models.CASCADE, verbose_name='Город')
    name = models.CharField('Имя', max_length=100)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    passport = models.CharField('Паспорт', max_length=50, null=True, blank=True)
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
    is_active = models.BooleanField('Работает', default=True)
    chat_id = models.CharField('ChatID', max_length=50, blank=True, null=True)
    note = models.TextField('Примечание', blank=True, null=True)
    login = models.CharField('Логин', max_length=50, unique=True)
    password = models.CharField('Пароль', max_length=100)
    
    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ['name']
        indexes = [
            models.Index(fields=['gorod', 'is_active']),
            models.Index(fields=['login']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.gorod})"
    
    @property
    def is_authenticated(self):
        return True
    
    def save(self, *args, **kwargs):
        # Получаем исходный пароль, если передан явно (например, из сериализатора)
        raw_password = kwargs.pop('raw_password', None)
        if not self.note:
            if raw_password:
                self.note = f'Логин: {self.login}, Пароль: {raw_password}'
            else:
                self.note = f'Логин: {self.login}'
        
        # Хешируем пароль при создании или изменении
        if self._state.adding:
            self.password = make_password(self.password)
        else:
            # Проверяем, изменился ли пароль
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                if old_instance.password != self.password:
                    self.password = make_password(self.password)
            except self.__class__.DoesNotExist:
                self.password = make_password(self.password)
        
        super().save(*args, **kwargs)

        # --- Синхронизация с Polzovateli ---
        if self.login and self.password:
            rol_master, _ = Roli.objects.get_or_create(name='master')
            # Создаем или обновляем пользователя только с нужными полями
            user_data = {
                'name': self.name,
                'password': self.password,
                'gorod': self.gorod,
                'rol': rol_master,
                'is_active': self.is_active,
            }
            user, created = Polzovateli.objects.get_or_create(
                login=self.login,
                defaults=user_data
            )
            if not created:
                # Обновляем данные пользователя, если мастер изменился
                user.name = self.name
                user.password = self.password
                user.gorod = self.gorod
                user.rol = rol_master
                user.is_active = self.is_active
                user.save()
