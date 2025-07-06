from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserSession, LoginAttempt


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа в систему"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Неверные учетные данные.')
            if not user.is_active:
                raise serializers.ValidationError('Пользователь заблокирован.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Необходимо указать имя пользователя и пароль.')
        
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Новые пароли не совпадают.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль.")
        return value


class UserSessionSerializer(serializers.ModelSerializer):
    """Сериализатор для сессий пользователей"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserSession
        fields = ['id', 'user', 'ip_address', 'user_agent', 'created_at', 'last_activity', 'is_active']
        read_only_fields = ['id', 'user', 'ip_address', 'user_agent', 'created_at', 'last_activity']


class LoginAttemptSerializer(serializers.ModelSerializer):
    """Сериализатор для попыток входа"""
    class Meta:
        model = LoginAttempt
        fields = ['id', 'username', 'ip_address', 'user_agent', 'success', 'created_at']
        read_only_fields = ['id', 'ip_address', 'user_agent', 'created_at'] 