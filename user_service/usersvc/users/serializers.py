"""
Сериализаторы для API микросервиса пользователей
"""

from rest_framework import serializers
from .models import Gorod, Roli, Polzovateli, Master


class GorodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gorod
        fields = ['id', 'name']


class RoliSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roli
        fields = ['id', 'name']


class PolzovateliSerializer(serializers.ModelSerializer):
    gorod = GorodSerializer(read_only=True)
    rol = RoliSerializer(read_only=True)
    gorod_id = serializers.IntegerField(write_only=True)
    rol_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Polzovateli
        fields = [
            'id', 'name', 'login', 'password', 'gorod', 'rol', 
            'is_active', 'note', 'gorod_id', 'rol_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        gorod_id = validated_data.pop('gorod_id')
        rol_id = validated_data.pop('rol_id')
        
        validated_data['gorod_id'] = gorod_id
        validated_data['rol_id'] = rol_id
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'gorod_id' in validated_data:
            instance.gorod_id = validated_data.pop('gorod_id')
        if 'rol_id' in validated_data:
            instance.rol_id = validated_data.pop('rol_id')
        
        return super().update(instance, validated_data)


class MasterSerializer(serializers.ModelSerializer):
    gorod = GorodSerializer(read_only=True)
    gorod_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Master
        fields = [
            'id', 'name', 'birth_date', 'passport', 'phone', 
            'is_active', 'chat_id', 'note', 'login', 'password', 
            'gorod', 'gorod_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        gorod_id = validated_data.pop('gorod_id')
        validated_data['gorod_id'] = gorod_id
        
        # Сохраняем исходный пароль для note
        raw_password = validated_data.get('password')
        instance = super().create(validated_data)
        
        # Обновляем note с паролем
        if raw_password and not instance.note:
            instance.note = f'Логин: {instance.login}, Пароль: {raw_password}'
            instance.save(update_fields=['note'])
        
        return instance
    
    def update(self, instance, validated_data):
        if 'gorod_id' in validated_data:
            instance.gorod_id = validated_data.pop('gorod_id')
        
        return super().update(instance, validated_data) 