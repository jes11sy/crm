from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
import logging
from django.conf import settings
from .models import Polzovateli, Master

logger = logging.getLogger(__name__)

class JWTCookieAuthentication(authentication.BaseAuthentication):
    """
    Кастомная аутентификация через JWT токены в cookies.
    """
    
    def authenticate(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            logger.debug('No JWT token found in cookies')
            return None
        
        try:
            # Декодируем JWT токен
            payload = jwt.decode(
                token, 
                getattr(settings, 'SECRET_KEY', 'devsecret'), 
                algorithms=['HS256']
            )
            
            logger.debug(f'JWT payload: {payload}')
            
            # Проверяем, есть ли user_id (пользователь) или master_id (мастер)
            if 'user_id' in payload:
                # Это пользователь
                user = Polzovateli.objects.get(id=payload['user_id'])
                
                # Проверяем активность пользователя
                if not user.is_active:
                    logger.warning(f'Inactive user: {user.login}')
                    raise AuthenticationFailed('Пользователь неактивен')
                
                # Добавляем роль в объект пользователя для удобства
                user.role = payload.get('role', '')
                
                logger.debug(f'Authenticated user: {user.login}, role: {user.role}')
                
                return (user, None)
                
            elif 'master_id' in payload:
                # Это мастер
                master = Master.objects.get(id=payload['master_id'])
                
                # Проверяем активность мастера
                if not master.is_active:
                    logger.warning(f'Inactive master: {master.login}')
                    raise AuthenticationFailed('Мастер неактивен')
                
                # Добавляем роль в объект мастера для удобства
                master.role = payload.get('role', 'master')
                
                logger.debug(f'Authenticated master: {master.login}, role: {master.role}')
                
                return (master, None)
                
            else:
                logger.warning(f'No user_id or master_id in JWT payload: {payload}')
                raise AuthenticationFailed('Невалидный токен: отсутствует идентификатор пользователя')
            
        except jwt.ExpiredSignatureError:
            logger.warning('JWT token expired')
            raise AuthenticationFailed('Токен истёк')
        except jwt.InvalidTokenError as e:
            logger.warning(f'Invalid JWT token: {e}')
            raise AuthenticationFailed('Невалидный токен')
        except Polzovateli.DoesNotExist:
            logger.warning(f'User not found for JWT payload: {payload}')
            raise AuthenticationFailed('Пользователь не найден')
        except Master.DoesNotExist:
            logger.warning(f'Master not found for JWT payload: {payload}')
            raise AuthenticationFailed('Мастер не найден')
        except Exception as e:
            logger.error(f'Authentication error: {e}')
            raise AuthenticationFailed(f'Ошибка аутентификации: {str(e)}')
    
    def authenticate_header(self, request):
        return 'JWT' 