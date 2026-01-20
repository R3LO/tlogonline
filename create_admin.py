#!/usr/bin/env python
"""
Скрипт для создания админ пользователя
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User

# Создаем суперпользователя из переменных окружения
username = os.getenv('ADMIN_USERNAME')
email = os.getenv('ADMIN_EMAIL')
password = os.getenv('ADMIN_PASSWORD')

try:
    # Проверяем, существует ли пользователь
    user = User.objects.get(username=username)
    print(f'Пользователь {username} уже существует')
except User.DoesNotExist:
    # Создаем нового пользователя
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'Суперпользователь {username} создан успешно!')
    print(f'Email: {email}')
    print(f'Пароль: {password}')

print('\nМожно войти в админ-панель: http://localhost:8000/admin/')