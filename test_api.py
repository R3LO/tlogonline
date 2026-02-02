#!/usr/bin/env python3
"""
Тест API для проверки функциональности QSO просмотра
"""
import requests
import json

def test_qso_api():
    """Тест API эндпоинта для получения QSO данных"""
    
    # URL для тестирования (нужно будет заменить на реальный после запуска сервера)
    base_url = "http://127.0.0.1:8000"
    
    # Сначала попробуем получить страницу LoTW
    try:
        response = requests.get(f"{base_url}/lotw/", allow_redirects=False)
        print(f"LoTW page status: {response.status_code}")
        if response.status_code == 302:
            print("Page requires authentication (normal)")
        elif response.status_code == 200:
            print("Page loaded successfully")
        else:
            print(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"Error accessing LoTW page: {e}")
    
    # Тест API эндпоинта (с тестовым ID)
    test_cases = [
        {"qso_id": "invalid-id"},
        {"qso_id": ""},
        # Можно добавить реальный ID после получения данных из БД
    ]
    
    for test_case in test_cases:
        try:
            response = requests.get(f"{base_url}/api/lotw/qso-details/", 
                                  params=test_case,
                                  allow_redirects=False)
            print(f"\nAPI test for {test_case}:")
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"Error response: {error_data}")
                except:
                    print(f"Raw response: {response.text}")
        except Exception as e:
            print(f"API test error: {e}")

if __name__ == "__main__":
    print("=== QSO API TEST ===")
    test_qso_api()
    print("=== TEST COMPLETE ===")