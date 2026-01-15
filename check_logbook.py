#!/usr/bin/env python3
"""
Скрипт для входа в систему и проверки логбука
"""
import requests
import time

def login_and_check_logbook():
    """Вход в систему и проверка логбука"""

    # Создаем сессию
    session = requests.Session()

    # Получаем CSRF токен
    login_url = 'http://127.0.0.1:8000/login/'
    response = session.get(login_url)

    # Извлекаем CSRF токен из cookies
    csrf_token = session.cookies.get('csrftoken')
    print(f"CSRF токен: {csrf_token}")

    # Данные для входа
    login_data = {
        'username': 'test_ham',
        'password': 'test123',
        'csrfmiddlewaretoken': csrf_token
    }

    # Заголовки
    headers = {
        'Referer': login_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Вход в систему
    print("Вход в систему...")
    response = session.post(login_url, data=login_data, headers=headers)

    if response.status_code == 200:
        print("Успешный вход в систему")

        # Переходим на страницу логбука
        logbook_url = 'http://127.0.0.1:8000/logbook/'
        print(f"Переходим на {logbook_url}")

        response = session.get(logbook_url)

        if response.status_code == 200:
            print("Успешный доступ к логбуку")
            print(f"Размер страницы: {len(response.content)} байт")

            # Проверяем, что в HTML нет примечаний
            content = response.text
            if 'fas fa-comment' in content:
                print("WARNING: Найдены иконки комментариев в HTML")
            else:
                print("OK: Иконки комментариев не найдены")

            if 'truncatechars:200' in content:
                print("WARNING: Найдены ссылки на truncatechars")
            else:
                print("OK: Ссылки на truncatechars не найдены")

            # Ищем таблицу QSO
            if '<table class="table table-striped' in content:
                print("OK: Найдена таблица QSO")
            else:
                print("WARNING: Таблица QSO не найдена")

            # Ищем колонки таблицы
            if '<th>' in content:
                print("OK: Найдены заголовки таблицы")
            else:
                print("WARNING: Заголовки таблицы не найдены")

            return True
        else:
            print(f"ERROR: Ошибка доступа к логбуку: {response.status_code}")
            return False
    else:
        print(f"ERROR: Ошибка входа: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return False

if __name__ == '__main__':
    login_and_check_logbook()