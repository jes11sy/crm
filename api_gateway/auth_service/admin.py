from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserSession, LoginAttempt


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для пользователей"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('phone',)}),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Админ-панель для сессий пользователей"""
    list_display = ['user', 'ip_address', 'created_at', 'last_activity', 'is_active']
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__username', 'user__email', 'ip_address']
    ordering = ['-last_activity']
    readonly_fields = ['created_at', 'last_activity']
    
    def has_add_permission(self, request):
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Админ-панель для попыток входа"""
    list_display = ['username', 'ip_address', 'success', 'created_at']
    list_filter = ['success', 'created_at']
    search_fields = ['username', 'ip_address']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
