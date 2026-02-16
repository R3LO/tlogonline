"""
Примеры тестирования REST API с Basic Authentication

Для работы с API необходимо:
1. Установить зависимости: pip install requests
2. Иметь действующего пользователя в системе
3. Использовать логин и пароль для Basic Authentication

Basic Authentication отправляет логин и пароль в заголовке Authorization:
Authorization: Basic base64(username:password)
"""

import requests
import base64
import json


# Конфигурация
BASE_URL = 'http://127.0.0.1:8000'
USERNAME = 'your_username'  # Замените на ваш логин
PASSWORD = 'your_password'  # Замените на ваш пароль


def get_auth_headers(username, password):
    """
    Создает заголовки с Basic Authentication
    """
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json'
    }


def test_get_user_info():
    """
    Тест: Получение информации о текущем пользователе
    """
    print("\n=== Тест 1: Получение информации о пользователе ===")
    url = f"{BASE_URL}/api/v1/user-info/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.get(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_get_profile():
    """
    Тест: Получение профиля пользователя
    """
    print("\n=== Тест 2: Получение профиля пользователя ===")
    url = f"{BASE_URL}/api/v1/profile/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.get(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_get_qsos():
    """
    Тест: Получение списка всех QSO пользователя
    """
    print("\n=== Тест 3: Получение списка QSO ===")
    url = f"{BASE_URL}/api/v1/qsos/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.get(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total QSO: {data.get('count', 0)}")
    if data.get('results'):
        print(f"First QSO: {json.dumps(data['results'][0], indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_get_qso_stats():
    """
    Тест: Получение статистики QSO
    """
    print("\n=== Тест 4: Получение статистики QSO ===")
    url = f"{BASE_URL}/api/v1/qsos/stats/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.get(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_search_qsos():
    """
    Тест: Поиск QSO по позывному
    """
    print("\n=== Тест 5: Поиск QSO по позывному ===")
    callsign = "UA"  # Частичное совпадение позывного
    url = f"{BASE_URL}/api/v1/qsos/search/?callsign={callsign}"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.get(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found QSO: {len(data) if isinstance(data, list) else 0}")
    if isinstance(data, list) and data:
        print(f"First result: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_get_qsos_by_band():
    """
    Тест: Получение QSO по диапазону
    """
    print("\n=== Тест 6: Получение QSO по диапазону ===")
    band = "20M"  # Диапазон
    url = f"{BASE_URL}/api/v1/qsos/by_band/?band={band}"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.get(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found QSO: {len(data) if isinstance(data, list) else 0}")
    if isinstance(data, list) and data:
        print(f"First result: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_get_single_qso(qso_id):
    """
    Тест: Получение конкретного QSO по ID
    """
    print(f"\n=== Тест 7: Получение QSO по ID ({qso_id}) ===")
    url = f"{BASE_URL}/api/v1/qsos/{qso_id}/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.get(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.json()}")
    return response.status_code == 200


def test_create_qso():
    """
    Тест: Создание нового QSO
    """
    print("\n=== Тест 8: Создание нового QSO ===")
    url = f"{BASE_URL}/api/v1/qsos/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    qso_data = {
        "date": "2025-01-15",
        "time": "14:30:00",
        "my_callsign": "UA0AAA",
        "callsign": "UA0BBB",
        "frequency": 14.070,
        "band": "20M",
        "mode": "FT8",
        "rst_sent": "599",
        "rst_rcvd": "599",
        "my_gridsquare": "KN88",
        "gridsquare": "KO85"
    }

    response = requests.post(url, headers=headers, json=qso_data)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"Created QSO: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.json()}")
    return response.status_code == 201


def test_update_qso(qso_id):
    """
    Тест: Обновление существующего QSO
    """
    print(f"\n=== Тест 9: Обновление QSO ({qso_id}) ===")
    url = f"{BASE_URL}/api/v1/qsos/{qso_id}/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    update_data = {
        "rst_sent": "579",
        "rst_rcvd": "579",
        "notes": "Updated via API"
    }

    response = requests.patch(url, headers=headers, json=update_data)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Updated QSO: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.json()}")
    return response.status_code == 200


def test_delete_qso(qso_id):
    """
    Тест: Удаление QSO
    """
    print(f"\n=== Тест 10: Удаление QSO ({qso_id}) ===")
    url = f"{BASE_URL}/api/v1/qsos/{qso_id}/"
    headers = get_auth_headers(USERNAME, PASSWORD)

    response = requests.delete(url, headers=headers)

    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("QSO deleted successfully")
    else:
        print(f"Error: {response.json()}")
    return response.status_code == 204


# ==================== CURL Примеры ====================

def print_curl_examples():
    """
    Печатает примеры CURL команд
    """
    print("\n" + "="*60)
    print("ПРИМЕРЫ CURL КОМАНД")
    print("="*60)

    credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()

    print(f"\n1. Получение информации о пользователе:")
    print(f'curl -X GET "{BASE_URL}/api/v1/user-info/" \\')
    print(f'  -H "Authorization: Basic {credentials}"')

    print(f"\n2. Получение профиля:")
    print(f'curl -X GET "{BASE_URL}/api/v1/profile/" \\')
    print(f'  -H "Authorization: Basic {credentials}"')

    print(f"\n3. Получение списка QSO:")
    print(f'curl -X GET "{BASE_URL}/api/v1/qsos/" \\')
    print(f'  -H "Authorization: Basic {credentials}"')

    print(f"\n4. Получение статистики QSO:")
    print(f'curl -X GET "{BASE_URL}/api/v1/qsos/stats/" \\')
    print(f'  -H "Authorization: Basic {credentials}"')

    print(f"\n5. Поиск QSO по позывному:")
    print(f'curl -X GET "{BASE_URL}/api/v1/qsos/search/?callsign=UA" \\')
    print(f'  -H "Authorization: Basic {credentials}"')

    print(f"\n6. Создание нового QSO:")
    print(f'curl -X POST "{BASE_URL}/api/v1/qsos/" \\')
    print(f'  -H "Authorization: Basic {credentials}" \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"date": "2025-01-15", "time": "14:30", "my_callsign": "UA0AAA", "callsign": "UA0BBB", "band": "20M", "mode": "FT8"}}\'')


if __name__ == '__main__':
    print("="*60)
    print("ТЕСТИРОВАНИЕ REST API")
    print("="*60)
    print(f"BASE_URL: {BASE_URL}")
    print(f"USERNAME: {USERNAME}")
    print(f"PASSWORD: {'*' * len(PASSWORD)}")

    # Запуск тестов
    results = []

    results.append(("Get User Info", test_get_user_info()))
    results.append(("Get Profile", test_get_profile()))
    results.append(("Get QSOs", test_get_qsos()))
    results.append(("Get QSO Stats", test_get_qso_stats()))
    results.append(("Search QSOs", test_search_qsos()))
    results.append(("Get QSOs by Band", test_get_qsos_by_band()))

    # Для тестов создания/обновления/удаления нужно иметь существующий QSO
    # results.append(("Create QSO", test_create_qso()))

    # Вывод результатов
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("="*60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    # Печать примеров CURL
    print_curl_examples()
