from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Расширенная модель пользователя"""
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.username} ({self.email})"


class UserSession(models.Model):
    """Модель для отслеживания сессий пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_user_sessions'
        verbose_name = 'Сессия пользователя'
        verbose_name_plural = 'Сессии пользователей'
    
    def __str__(self):
        return f"Session for {self.user.username} at {self.created_at}"


class LoginAttempt(models.Model):
    """Модель для отслеживания попыток входа"""
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_login_attempts'
        verbose_name = 'Попытка входа'
        verbose_name_plural = 'Попытки входа'
    
    def __str__(self):
        status = "Успешно" if self.success else "Неудачно"
        return f"{self.username} - {status} - {self.created_at}"
