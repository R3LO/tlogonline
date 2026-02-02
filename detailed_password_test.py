#!/usr/bin/env python3
"""
Детальная проверка смены пароля с проверкой хешей в базе данных
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
from django.db import connection

def test_password_hash_change():
    """Детальный тест смены пароля с проверкой хешей"""
    
    print("🔍 Создание тестового пользователя...")
    
    # Создаем тестового пользователя
    try:
        user = User.objects.create_user(
            username='testuser_hash',
            email='test@example.com',
            password='oldpassword123'
        )
        print(f"✅ Пользователь создан: {user.username}")
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        return
    
    # Получаем хеш исходного пароля из базы данных
    with connection.cursor() as cursor:
        cursor.execute("SELECT password FROM auth_user WHERE username = %s", [user.username])
        original_hash = cursor.fetchone()[0]
        print(f"🔑 Исходный хеш пароля: {original_hash[:50]}...")
    
    # Создаем клиент и авторизуемся
    client = Client()
    client.force_login(user)
    
    print("\n🔍 Проверка авторизации с исходным паролем...")
    
    # Проверяем, что можем авторизоваться с исходным паролем
    test_user = User.objects.get(username='testuser_hash')
    if test_user.check_password('oldpassword123'):
        print("✅ Авторизация с исходным паролем работает")
    else:
        print("❌ Авторизация с исходным паролем НЕ работает")
    
    print("\n📝 Выполнение смены пароля...")
    
    # Выполняем смену пароля
    response = client.post('/profile/change-password/', {
        'old_password': 'oldpassword123',
        'new_password': 'newpassword456',
        'confirm_password': 'newpassword456'
    })
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Перенаправление на: {response.url}")
    
    # Получаем хеш нового пароля из базы данных
    with connection.cursor() as cursor:
        cursor.execute("SELECT password FROM auth_user WHERE username = %s", [user.username])
        new_hash = cursor.fetchone()[0]
        print(f"🔑 Новый хеш пароля: {new_hash[:50]}...")
    
    print("\n🔍 Проверка изменений в базе данных...")
    
    # Проверяем, что хеш изменился
    if original_hash != new_hash:
        print("✅ Хеш пароля изменился в базе данных!")
    else:
        print("❌ Хеш пароля НЕ изменился в базе данных!")
    
    # Обновляем объект пользователя из базы
    user.refresh_from_db()
    
    # Проверяем, что старый пароль больше не работает
    if not user.check_password('oldpassword123'):
        print("✅ Старый пароль больше НЕ работает")
    else:
        print("❌ Старый пароль все еще работает (ошибка!)")
    
    # Проверяем, что новый пароль работает
    if user.check_password('newpassword456'):
        print("✅ Новый пароль работает!")
    else:
        print("❌ Новый пароль НЕ работает (ошибка!)")
    
    # Проверяем, что пользователь все еще авторизован (благодаря update_session_auth_hash)
    print("\n🔍 Проверка сессии пользователя...")
    response = client.get('/profile/')
    if response.status_code == 200:
        print("✅ Пользователь остался авторизован после смены пароля")
    else:
        print(f"❌ Пользователь разлогинился после смены пароля (статус: {response.status_code})")
    
    print("\n🔍 Проверка структуры хеша пароля...")
    
    # Проверяем, что хеш хранится в правильном формате Django
    if new_hash.startswith('pbkdf2_sha256$'):
        print("✅ Хеш хранится в правильном формате Django (pbkdf2_sha256)")
    elif new_hash.startswith('bcrypt$'):
        print("✅ Хеш хранится в формате bcrypt")
    elif new_hash.startswith('argon2$'):
        print("✅ Хеш хранится в формате argon2")
    else:
        print(f"⚠️  Неизвестный формат хеша: {new_hash[:20]}...")
    
    # Показываем детали хеша
    if new_hash.startswith('pbkdf2_sha256$'):
        parts = new_hash.split('$')
        if len(parts) >= 4:
            iterations = parts[1]
            salt = parts[2][:16] + "..."
            hash_part = parts[3][:16] + "..."
            print(f"   - Итерации: {iterations}")
            print(f"   - Соль: {salt}")
            print(f"   - Хеш: {hash_part}")
    
    print("\n🎉 Детальное тестирование завершено!")
    
    # Очистка
    try:
        user.delete()
        print("🧹 Тестовый пользователь удален")
    except:
        pass

if __name__ == '__main__':
    test_password_hash_change()