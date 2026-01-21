"""
Настройки админки для приложения tlog (Django 5.2)
"""
from django.contrib import admin
from .models import RadioProfile


@admin.register(RadioProfile)
class RadioProfileAdmin(admin.ModelAdmin):
    list_display = ('callsign', 'user', 'my_gridsquare', 'first_name', 'last_name', 'qth', 'is_blocked', 'created_at')
    list_filter = ('created_at', 'is_blocked')
    search_fields = ('callsign', 'user__username', 'user__email', 'my_gridsquare', 'first_name', 'last_name', 'qth', 'my_callsigns')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'blocked_at')

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Радиолюбительская информация', {
            'fields': ('callsign', 'my_gridsquare')
        }),
        ('Мои позывные', {
            'fields': ('my_callsigns',),
            'description': 'Бывшие, действующие, спецпозывные, позывные с дробями'
        }),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'qth')
        }),
        ('Блокировка', {
            'fields': ('is_blocked', 'blocked_reason', 'blocked_at'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name = 'Регистрация пользователей'
        verbose_name_plural = 'Регистрация пользователей'