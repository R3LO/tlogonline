#!/usr/bin/env python3
"""
Полный тест смены пароля через веб-интерфейс с авторизацией
"""

import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client

def test_full_password_change():
    """Полный тест смены пароля через веб-интерфейс"""
    
    print("🔧 Подготовка тестового пользователя...")
    
    # Создаем тестового пользователя
    try:
        # Удаляем старого тестового пользователя если есть
        User.objects.filter(username='webtest').delete()
        
        user = User.objects.create_user(
            username='webtest',
            email='webtest@example.com',
            password='oldpassword123'
        )
        print(f"✅ Пользователь создан: {user.username}")
        print(f"🔑 Исходный хеш: {user.password[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        return
    
    print("\n🌐 Тестирование через веб-интерфейс...")
    
    # Создаем Django тестовый клиент
    client = Client()
    
    # Авторизуемся
    login_success = client.login(username='webtest', password='oldpassword123')
    if login_success:
        print("✅ Авторизация успешна")
    else:
        print("❌ Авторизация не удалась")
        return
    
    print("\n1. Доступ к странице профиля...")
    response = client.get('/profile/')
    print(f"   Статус: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Не удалось получить доступ к странице профиля")
        return
    
    # Парсим HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("\n2. Поиск элементов смены пароля...")
    
    # Ищем кнопку смены пароля
    password_button = soup.find('button', string=lambda text: text and 'Сменить пароль' in text)
    if password_button:
        print("   ✅ Кнопка 'Сменить пароль' найдена")
        print(f"   Атрибуты кнопки: {password_button.attrs}")
    else:
        print("   ❌ Кнопка 'Сменить пароль' НЕ найдена")
        
        # Ищем любое упоминание пароля
        password_text = soup.find(string=lambda text: text and 'пароль' in text.lower())
        if password_text:
            print(f"   🔍 Найден текст с 'пароль': {password_text.strip()[:100]}...")
    
    # Ищем форму смены пароля
    password_form = soup.find('form', action='/profile/change-password/')
    if password_form:
        print("   ✅ Форма смены пароля найдена")
        
        # Ищем CSRF токен
        csrf_token = password_form.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_token:
            print("   ✅ CSRF токен найден")
        else:
            print("   ❌ CSRF токен НЕ найден")
            
        # Ищем поля ввода
        fields = {
            'old_password': password_form.find('input', {'name': 'old_password'}),
            'new_password': password_form.find('input', {'name': 'new_password'}),
            'confirm_password': password_form.find('input', {'name': 'confirm_password'})
        }
        
        for field_name, field in fields.items():
            if field:
                print(f"   ✅ Поле '{field_name}' найдено")
            else:
                print(f"   ❌ Поле '{field_name}' НЕ найдено")
    else:
        print("   ❌ Форма смены пароля НЕ найдена")
        
        # Ищем все формы
        all_forms = soup.find_all('form')
        print(f"   🔍 Всего найдено форм: {len(all_forms)}")
        for i, form in enumerate(all_forms):
            action = form.get('action', 'Нет action')
            print(f"      Форма {i+1}: action='{action}'")
    
    print("\n3. Выполнение смены пароля...")
    
    # Получаем CSRF токен из cookies
    csrftoken = client.cookies['csrftoken']
    
    # Данные для смены пароля
    password_data = {
        'csrfmiddlewaretoken': csrftoken,
        'old_password': 'oldpassword123',
        'new_password': 'newpassword456',
        'confirm_password': 'newpassword456'
    }
    
    # Отправляем запрос на смену пароля
    response = client.post('/profile/change-password/', password_data)
    print(f"   Статус ответа: {response.status_code}")
    print(f"   Перенаправление на: {response.url}")
    
    # Проверяем результат в базе данных
    user.refresh_from_db()
    print(f"🔑 Новый хеш в БД: {user.password[:50]}...")
    
    if user.check_password('newpassword456'):
        print("✅ Новый пароль работает!")
    else:
        print("❌ Новый пароль НЕ работает")
        
    if not user.check_password('oldpassword123'):
        print("✅ Старый пароль больше не работает")
    else:
        print("❌ Старый пароль все еще работает")
    
    print("\n4. Проверка авторизации после смены пароля...")
    
    # Проверяем, что можем авторизоваться с новым паролем
    new_login_success = client.login(username='webtest', password='newpassword456')
    if new_login_success:
        print("✅ Авторизация с новым паролем работает")
    else:
        print("❌ Авторизация с новым паролем НЕ работает")
    
    # Проверяем, что старый пароль не работает
    old_login_success = client.login(username='webtest', password='oldpassword123')
    if not old_login_success:
        print("✅ Авторизация со старым паролем не работает (правильно)")
    else:
        print("❌ Авторизация со старым паролем все еще работает (ошибка!)")
    
    print("\n5. Очистка...")
    
    # Удаляем тестового пользователя
    try:
        user.delete()
        print("🧹 Тестовый пользователь удален")
    except Exception as e:
        print(f"❌ Ошибка удаления пользователя: {e}")
    
    print("\n🎉 Полное тестирование завершено!")

if __name__ == '__main__':
    test_full_password_change()