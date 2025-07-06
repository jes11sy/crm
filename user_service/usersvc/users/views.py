"""
Views для API микросервиса пользователей
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from .models import Gorod, Roli, Polzovateli, Master
from .serializers import (
    GorodSerializer, RoliSerializer, 
    PolzovateliSerializer, MasterSerializer
)


class GorodViewSet(viewsets.ModelViewSet):
    queryset = Gorod.objects.all()
    serializer_class = GorodSerializer
    # Используем настройки по умолчанию (IsAuthenticated)
    
    def get_queryset(self):
        return Gorod.objects.all().order_by('name')


class RoliViewSet(viewsets.ModelViewSet):
    queryset = Roli.objects.all()
    serializer_class = RoliSerializer
    # Используем настройки по умолчанию (IsAuthenticated)
    
    def get_queryset(self):
        return Roli.objects.all().order_by('name')


class PolzovateliViewSet(viewsets.ModelViewSet):
    queryset = Polzovateli.objects.all()
    serializer_class = PolzovateliSerializer
    # Используем настройки по умолчанию (IsAuthenticated)
    
    def get_queryset(self):
        queryset = Polzovateli.objects.select_related('gorod', 'rol')
        
        # Фильтрация по городу
        gorod_id = self.request.query_params.get('gorod_id')
        if gorod_id:
            queryset = queryset.filter(gorod_id=gorod_id)
        
        # Фильтрация по роли
        rol_id = self.request.query_params.get('rol_id')
        if rol_id:
            queryset = queryset.filter(rol_id=rol_id)
        
        # Фильтрация по статусу
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    @action(detail=False, methods=['post'])
    def authenticate(self, request):
        """Аутентификация пользователя"""
        login = request.data.get('login')
        password = request.data.get('password')
        
        if not login or not password:
            return Response(
                {'error': 'Необходимо указать логин и пароль'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = Polzovateli.objects.select_related('gorod', 'rol').get(login=login)
            
            if not user.is_active:
                return Response(
                    {'error': 'Пользователь неактивен'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if check_password(password, user.password):
                serializer = self.get_serializer(user)
                return Response({
                    'user': serializer.data,
                    'authenticated': True
                })
            else:
                return Response(
                    {'error': 'Неверный пароль'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Polzovateli.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    # Используем настройки по умолчанию (IsAuthenticated)
    
    def get_queryset(self):
        queryset = Master.objects.select_related('gorod')
        
        # Фильтрация по городу
        gorod_id = self.request.query_params.get('gorod_id')
        if gorod_id:
            queryset = queryset.filter(gorod_id=gorod_id)
        
        # Фильтрация по статусу
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    @action(detail=False, methods=['post'])
    def authenticate(self, request):
        """Аутентификация мастера"""
        login = request.data.get('login')
        password = request.data.get('password')
        
        if not login or not password:
            return Response(
                {'error': 'Необходимо указать логин и пароль'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            master = Master.objects.select_related('gorod').get(login=login)
            
            if not master.is_active:
                return Response(
                    {'error': 'Мастер неактивен'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if check_password(password, master.password):
                serializer = self.get_serializer(master)
                return Response({
                    'master': serializer.data,
                    'authenticated': True
                })
            else:
                return Response(
                    {'error': 'Неверный пароль'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Master.DoesNotExist:
            return Response(
                {'error': 'Мастер не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
