#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функции смены пароля
Запуск: python test_password_change.py
"""

import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tlog.settings')
django.setup()

from django.contrib.auth.models import User
from tlog.models import RadioProfile

def test_password_change():
    """Тестирование функции смены пароля"""
    
    print("🧪 Тестирование функции смены пароля")
    print("=" * 60)
    
    # Создаем тестового пользователя
    try:
        test_user, created = User.objects.get_or_create(
            username='test_user_password',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            }
        )
        
        if created:
            test_user.set_password('oldpassword123')
            test_user.save()
            print("✅ Создан тестовый пользователь с паролем 'oldpassword123'")
        else:
            print("ℹ️ Используется существующий пользователь")
            
        print(f"📊 Тестовый пользователь:")
        print(f"   - Имя: {test_user.username}")
        print(f"   - Email: {test_user.email}")
        print(f"   - Хеш пароля: {test_user.password[:20]}...")
        
        # Тестируем смену пароля напрямую через Django
        print("\n🔬 Тест 1: Смена пароля через Django")
        
        old_password = 'oldpassword123'
        new_password = 'newpassword456'
        
        # Проверяем старый пароль
        if not test_user.check_password(old_password):
            print("❌ Текущий пароль неверный!")
            return False
        
        print("✅ Текущий пароль верный")
        
        # Устанавливаем новый пароль
        test_user.set_password(new_password)
        test_user.save()
        
        print("✅ Новый пароль установлен")
        
        # Проверяем что пароль изменился
        test_user.refresh_from_db()
        
        if test_user.check_password(new_password):
            print("✅ Новый пароль работает!")
        else:
            print("❌ Новый пароль не работает!")
            return False
            
        if not test_user.check_password(old_password):
            print("✅ Старый пароль больше не работает!")
        else:
            print("❌ Старый пароль все еще работает!")
            return False
        
        print("\n🔬 Тест 2: Проверка Django функции change_password")
        
        # Импортируем функцию из views
        from tlog.views.profile import change_password
        from django.test import RequestFactory
        
        factory = RequestFactory()
        
        # Создаем POST запрос
        request = factory.post('/profile/change-password/', {
            'old_password': new_password,
            'new_password': 'thirdpassword789',
            'confirm_password': 'thirdpassword789'
        })
        request.user = test_user
        
        print("📤 Отправляем запрос на смену пароля...")
        
        try:
            response = change_password(request)
            print(f"✅ Функция change_password выполнена без ошибок")
            print(f"   Response type: {type(response)}")
            
            # Проверяем что пароль изменился
            test_user.refresh_from_db()
            
            if test_user.check_password('thirdpassword789'):
                print("✅ Пароль успешно изменен через функцию!")
            else:
                print("❌ Пароль не изменился через функцию!")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при выполнении функции change_password: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🔬 Тест 3: Проверка хеширования пароля")
        
        # Проверяем что пароль правильно хеширован
        print(f"   Хеш пароля: {test_user.password}")
        
        # Проверяем что хеш изменился
        if 'pbkdf2_sha256' in test_user.password:
            print("✅ Пароль правильно хеширован через PBKDF2")
        else:
            print("⚠️ Неожиданный формат хеша пароля")
        
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Функция смены пароля работает корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Очистка тестовых данных"""
    print("🧹 Очистка тестовых данных...")
    
    try:
        User.objects.filter(username='test_user_password').delete()
        print("✅ Тестовые данные удалены")
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

if __name__ == "__main__":
    print("Запуск тестирования функции смены пароля...")
    print()
    
    # Выполняем тесты
    success = test_password_change()
    
    if success:
        print("\n" + "="*60)
        print("Хотите удалить тестовые данные? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice in ['y', 'yes', 'да', 'д']:
            cleanup_test_data()
    else:
        print("❌ Тестирование завершилось с ошибками")
        sys.exit(1)
