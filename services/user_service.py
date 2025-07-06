"""
Сервис для работы с пользователями и аутентификацией.
В будущем может быть выделен в отдельный микросервис.
"""

import jwt
import logging
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from core.models import Polzovateli, Master
from core.serializers import PolzovateliSerializer, MasterSerializer

logger = logging.getLogger(__name__)

class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def authenticate_user(login, password):
        """Аутентификация пользователя"""
        try:
            # Сначала пробуем найти обычного пользователя
            user = Polzovateli.objects.filter(login=login, is_active=True).first()
            if user and user.check_password(password):
                return user, 'user'
            
            # Затем пробуем найти мастера
            master = Master.objects.filter(login=login, is_active=True).first()
            if master and master.check_password(password):
                return master, 'master'
            
            return None, None
            
        except Exception as e:
            logger.error(f"Ошибка аутентификации: {e}")
            return None, None
    
    @staticmethod
    def create_jwt_token(user, user_type):
        """Создание JWT токена"""
        try:
            if user_type == 'user':
                payload = {
                    'user_id': user.id,
                    'login': user.login,
                    'role': user.rol.name,
                    'type': 'user'
                }
            else:  # master
                payload = {
                    'master_id': user.id,
                    'login': user.login,
                    'role': 'master',
                    'type': 'master'
                }
            
            token = jwt.encode(
                payload,
                getattr(settings, 'SECRET_KEY', 'devsecret'),
                algorithm='HS256'
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Ошибка создания JWT токена: {e}")
            return None
    
    @staticmethod
    def get_user_info(user, user_type):
        """Получение информации о пользователе"""
        try:
            if user_type == 'user':
                return {
                    'id': user.id,
                    'name': user.name,
                    'role': user.rol.name,
                    'login': user.login,
                    'gorod_id': user.gorod.id if user.gorod else None,
                    'is_active': user.is_active,
                    'type': 'user'
                }
            else:  # master
                return {
                    'id': user.id,
                    'name': user.name,
                    'role': 'master',
                    'login': user.login,
                    'gorod_id': user.gorod.id if user.gorod else None,
                    'is_active': user.is_active,
                    'type': 'master'
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            return None

class AuthService:
    """Сервис аутентификации"""
    
    @staticmethod
    def login(login, password):
        """Вход в систему"""
        user, user_type = UserService.authenticate_user(login, password)
        
        if not user:
            return {
                'success': False,
                'error': 'Неверный логин или пароль',
                'code': 'INVALID_CREDENTIALS'
            }
        
        token = UserService.create_jwt_token(user, user_type)
        if not token:
            return {
                'success': False,
                'error': 'Ошибка создания токена',
                'code': 'TOKEN_CREATION_ERROR'
            }
        
        user_info = UserService.get_user_info(user, user_type)
        
        return {
            'success': True,
            'token': token,
            'user': user_info
        }
    
    @staticmethod
    def logout():
        """Выход из системы"""
        return {
            'success': True,
            'message': 'Успешный выход из системы'
        } 