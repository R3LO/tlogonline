#!/usr/bin/env python3
"""
Тест для проверки функциональности смены пароля в Django приложении
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

class PasswordChangeTest(TestCase):
    """Тесты для функциональности смены пароля"""
    
    def setUp(self):
        """Создание тестового пользователя"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        self.client = Client()
        self.client.force_login(self.user)
        
        # URL для смены пароля
        self.change_password_url = reverse('change_password')
        
    def test_change_password_page_accessible(self):
        """Тест доступности страницы смены пароля"""
        response = self.client.get('/profile/change-password/')
        self.assertEqual(response.status_code, 200)  # Страница должна загружаться
        
    def test_change_password_valid_old_password(self):
        """Тест смены пароля с правильным текущим паролем"""
        response = self.client.post('/profile/change-password/', {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        })
        
        # Проверяем, что пользователь перенаправляется обратно на профиль
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.url.endswith('/profile/'))
        
        # Проверяем, что новый пароль работает
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('newpassword456'))
        self.assertFalse(user.check_password('oldpassword123'))
        
    def test_change_password_invalid_old_password(self):
        """Тест смены пароля с неправильным текущим паролем"""
        response = self.client.post('/profile/change-password/', {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        })
        
        # Должны остаться на той же странице с ошибкой
        self.assertEqual(response.status_code, 302)  # Redirect back to profile
        self.assertTrue(response.url.endswith('/profile/'))
        
        # Старый пароль должен остаться активным
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('oldpassword123'))
        self.assertFalse(user.check_password('newpassword456'))
        
    def test_change_password_mismatched_confirmation(self):
        """Тест смены пароля с несовпадающим подтверждением"""
        response = self.client.post('/profile/change-password/', {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'differentpassword'
        })
        
        # Должны остаться на той же странице
        self.assertEqual(response.status_code, 302)  # Redirect back to profile
        
        # Пароль не должен измениться
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('oldpassword123'))
        self.assertFalse(user.check_password('newpassword456'))
        
    def test_change_password_too_short(self):
        """Тест смены пароля на слишком короткий пароль"""
        response = self.client.post('/profile/change-password/', {
            'old_password': 'oldpassword123',
            'new_password': 'short',
            'confirm_password': 'short'
        })
        
        # Должны остаться на той же странице
        self.assertEqual(response.status_code, 302)  # Redirect back to profile
        
        # Пароль не должен измениться
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('oldpassword123'))
        self.assertFalse(user.check_password('short'))
        
    def test_change_password_empty_fields(self):
        """Тест смены пароля с пустыми полями"""
        response = self.client.post('/profile/change-password/', {
            'old_password': '',
            'new_password': '',
            'confirm_password': ''
        })
        
        # Должны остаться на той же странице
        self.assertEqual(response.status_code, 302)  # Redirect back to profile
        
        # Пароль не должен измениться
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('oldpassword123'))

def run_tests():
    """Запуск тестов"""
    print("Запуск тестов функциональности смены пароля...")
    print("=" * 50)
    
    # Создаем тестовый набор
    test_suite = TestCase.defaultTestLoader.loadTestsFromTestCase(PasswordChangeTest)
    
    # Запускаем тесты
    runner = TestCase.runner
    runner.run(test_suite)

if __name__ == '__main__':
    run_tests()