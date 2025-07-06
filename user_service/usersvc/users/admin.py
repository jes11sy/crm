"""
Админ-панель для моделей пользователей
"""

from django.contrib import admin
from .models import Gorod, Roli, Polzovateli, Master


@admin.register(Gorod)
class GorodAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Roli)
class RoliAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Polzovateli)
class PolzovateliAdmin(admin.ModelAdmin):
    list_display = ['name', 'login', 'gorod', 'rol', 'is_active']
    list_filter = ['gorod', 'rol', 'is_active']
    search_fields = ['name', 'login']
    ordering = ['name']
    readonly_fields = ['password']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('gorod', 'rol')


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['name', 'login', 'gorod', 'phone', 'is_active']
    list_filter = ['gorod', 'is_active']
    search_fields = ['name', 'login', 'phone']
    ordering = ['name']
    readonly_fields = ['password']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('gorod')
