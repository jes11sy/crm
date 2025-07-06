from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from ..models import Master, Roli, Polzovateli
from ..serializers import MasterSerializer, RoliSerializer, PolzovateliSerializer
from ..permissions import IsCallCentreOrAbove, IsAdminOnly, IsDirectorOrAdmin, IsSameCity, IsKCUserOrAbove
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.conf import settings
import jwt
import logging
from ..utils import send_business_alert

logger = logging.getLogger(__name__)

class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.select_related('gorod')
    serializer_class = MasterSerializer
    permission_classes = [IsCallCentreOrAbove, IsSameCity]
    filterset_fields = ['name', 'gorod', 'is_active', 'phone']
    search_fields = ['name', 'phone', 'login']
    ordering_fields = ['name', 'created_at']
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
        if hasattr(user, 'gorod_id'):
            return queryset.filter(gorod_id=user.gorod_id)
        return queryset
    @action(detail=False, methods=['get'])
    def active(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class RoliViewSet(viewsets.ModelViewSet):
    queryset = Roli.objects.all()
    serializer_class = RoliSerializer
    permission_classes = [IsAdminOnly]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']

class PolzovateliViewSet(viewsets.ModelViewSet):
    queryset = Polzovateli.objects.select_related('gorod', 'rol')
    serializer_class = PolzovateliSerializer
    permission_classes = [IsDirectorOrAdmin]
    filterset_fields = ['name', 'gorod', 'rol', 'is_active']
    search_fields = ['name', 'login']
    ordering_fields = ['name', 'created_at']
    @action(detail=False, methods=['get'])
    def active(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@extend_schema(
    summary="Аутентификация пользователя",
    description="Вход в систему для пользователей и мастеров",
    tags=['auth'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'login': {'type': 'string', 'description': 'Логин пользователя'},
                'password': {'type': 'string', 'description': 'Пароль пользователя'}
            },
            'required': ['login', 'password']
        }
    },
    responses={
        200: {
            'description': 'Успешная аутентификация',
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'role': {'type': 'string'},
                'name': {'type': 'string'}
            }
        },
        400: {'description': 'Неверные данные'},
        401: {'description': 'Неверный логин или пароль'}
    }
)
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')
        
        if not login or not password:
            return Response({'error': 'Необходимо указать логин и пароль'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Сначала пробуем найти пользователя
            user = Polzovateli.objects.get(login=login, is_active=True)
            if check_password(password, user.password):
                # Создаем JWT токен
                payload = {
                    'user_id': user.id,
                    'login': user.login,
                    'role': user.rol.name,
                    'gorod_id': user.gorod.id,
                    'exp': timezone.now() + timezone.timedelta(days=1)
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                
                response = Response({
                    'success': True,
                    'role': user.rol.name,
                    'name': user.name,
                    'token': token
                })
                response.set_cookie(
                    'jwt', token, 
                    max_age=86400, 
                    httponly=True, 
                    secure=not settings.DEBUG,  # Secure только в продакшн
                    samesite='Strict'  # Защита от CSRF
                )
                
                # Отправляем алерт о входе пользователя
                if getattr(settings, 'TELEGRAM_BUSINESS_ALERTS', True):
                    send_business_alert(
                        event_type='login',
                        description=f'Пользователь {user.name} вошел в систему',
                        user_info=f'{user.login} ({user.rol.name})',
                        additional_data={
                            'gorod': user.gorod.name if user.gorod else 'Не указан',
                            'ip_address': request.META.get('REMOTE_ADDR', ''),
                            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100]
                        }
                    )
                
                return response
        except Polzovateli.DoesNotExist:
            pass
        
        try:
            # Если пользователь не найден, пробуем найти мастера
            master = Master.objects.get(login=login, is_active=True)
            if check_password(password, master.password):
                # Создаем JWT токен для мастера
                payload = {
                    'master_id': master.id,
                    'login': master.login,
                    'role': 'master',
                    'gorod_id': master.gorod.id,
                    'exp': timezone.now() + timezone.timedelta(days=1)
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                
                response = Response({
                    'success': True,
                    'role': 'master',
                    'name': master.name,
                    'token': token
                })
                response.set_cookie(
                    'jwt', token, 
                    max_age=86400, 
                    httponly=True, 
                    secure=not settings.DEBUG,  # Secure только в продакшн
                    samesite='Strict'  # Защита от CSRF
                )
                
                # Отправляем алерт о входе мастера
                if getattr(settings, 'TELEGRAM_BUSINESS_ALERTS', True):
                    send_business_alert(
                        event_type='login',
                        description=f'Мастер {master.name} вошел в систему',
                        user_info=f'{master.login} (master)',
                        additional_data={
                            'gorod': master.gorod.name if master.gorod else 'Не указан',
                            'ip_address': request.META.get('REMOTE_ADDR', ''),
                            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100]
                        }
                    )
                
                return response
        except Master.DoesNotExist:
            pass
        
        return Response({'error': 'Неверный логин или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    summary="Выход из системы",
    description="Выход пользователя из системы с очисткой cookies",
    tags=['auth'],
    responses={
        200: {
            'description': 'Успешный выход',
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'}
            }
        }
    }
)
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        response = Response({'success': True})
        response.delete_cookie('jwt')
        return response

class ClearCookiesView(APIView):
    """Принудительная очистка cookies"""
    permission_classes = []
    def post(self, request):
        response = Response({'success': True})
        response.delete_cookie('jwt')
        return response

@extend_schema(
    summary="Информация о текущем пользователе",
    description="Получение информации о текущем аутентифицированном пользователе или мастере",
    tags=['auth'],
    responses={
        200: {
            'description': 'Информация о пользователе',
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'role': {'type': 'string'},
                'login': {'type': 'string'},
                'gorod_id': {'type': 'integer'},
                'is_active': {'type': 'boolean'}
            }
        },
        401: {'description': 'Не авторизован'}
    }
)
class MeView(APIView):
    def get(self, request):
        user = request.user
        
        if hasattr(user, 'id') and hasattr(user, 'rol'):
            # Это пользователь (Polzovateli)
            return Response({
                'id': user.id,
                'name': user.name,
                'role': user.rol.name,
                'login': user.login,
                'gorod_id': user.gorod.id,
                'is_active': user.is_active
            })
        elif hasattr(user, 'id') and hasattr(user, 'role'):
            # Это мастер (Master)
            return Response({
                'id': user.id,
                'name': user.name,
                'role': user.role,
                'login': user.login,
                'gorod_id': user.gorod.id,
                'is_active': user.is_active
            })
        else:
            return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED) 