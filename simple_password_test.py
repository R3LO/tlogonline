#!/usr/bin/env python3
"""
Простой тест для проверки функциональности смены пароля
"""

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_password_change():
    """Тест функции смены пароля"""
    
    print("🔍 Создание тестового пользователя...")
    
    # Создаем тестового пользователя
    try:
        user = User.objects.create_user(
            username='testuser123',
            email='test@example.com',
            password='oldpassword123'
        )
        print(f"✅ Пользователь создан: {user.username}")
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        return
    
    # Создаем клиент и авторизуемся
    client = Client()
    client.force_login(user)
    
    print("🔍 Тестирование смены пароля...")
    
    # Тест 1: Успешная смена пароля
    print("\n📝 Тест 1: Успешная смена пароля")
    response = client.post('/profile/change-password/', {
        'old_password': 'oldpassword123',
        'new_password': 'newpassword456',
        'confirm_password': 'newpassword456'
    })
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Перенаправление на: {response.url}")
    
    # Проверяем, что пароль изменился
    user.refresh_from_db()
    if user.check_password('newpassword456'):
        print("✅ Пароль успешно изменен!")
    else:
        print("❌ Пароль НЕ изменился!")
    
    # Тест 2: Неправильный текущий пароль
    print("\n📝 Тест 2: Неправильный текущий пароль")
    response = client.post('/profile/change-password/', {
        'old_password': 'wrongpassword',
        'new_password': 'anotherpassword123',
        'confirm_password': 'anotherpassword123'
    })
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Перенаправление на: {response.url}")
    
    # Проверяем, что пароль НЕ изменился
    user.refresh_from_db()
    if user.check_password('newpassword456'):
        print("✅ Пароль остался прежним (правильно)")
    else:
        print("❌ Что-то пошло не так с паролем")
    
    # Тест 3: Несовпадающие пароли
    print("\n📝 Тест 3: Несовпадающие пароли")
    response = client.post('/profile/change-password/', {
        'old_password': 'newpassword456',
        'new_password': 'password123',
        'confirm_password': 'differentpassword'
    })
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Перенаправление на: {response.url}")
    
    # Тест 4: Слишком короткий пароль
    print("\n📝 Тест 4: Слишком короткий пароль")
    response = client.post('/profile/change-password/', {
        'old_password': 'newpassword456',
        'new_password': 'short',
        'confirm_password': 'short'
    })
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Перенаправление на: {response.url}")
    
    print("\n🎉 Тестирование завершено!")
    
    # Очистка
    try:
        user.delete()
        print("🧹 Тестовый пользователь удален")
    except:
        pass

if __name__ == '__main__':
    test_password_change()