#!/usr/bin/env python
"""
Скрипт для создания тестового радиолюбителя
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from frontend.models import RadioProfile

# Создаем тестового радиолюбителя
username = 'test_ham'
email = 'test@example.com'
password = 'testpass123'
callsign = 'UA1ABC'
qth_locator = 'KO85UU'
city = 'Москва'
country = 'Россия'

try:
    # Проверяем, существует ли пользователь
    user = User.objects.get(username=username)
    print(f'Пользователь {username} уже существует')
except User.DoesNotExist:
    # Создаем нового пользователя
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Иван',
        last_name='Петров'
    )
    print(f'Пользователь {username} создан успешно!')

    # Создаем профиль радиолюбителя
    profile = RadioProfile.objects.create(
        user=user,
        callsign=callsign,
        name=f'{user.first_name} {user.last_name}',
        location=f'{city}, {country}',
        license_class='1'
    )
    print(f'Профиль радиолюбителя {callsign} создан успешно!')

print(f'''
Тестовый радиолюбитель готов:
Логин: {username}
Пароль: {password}
Позывной: {callsign}
QTH: {qth_locator}
''')