"""
Тестовый скрипт для проверки работы API клиента
"""
from rest_api_client.api_client import APIClient


def test_api():
    """Тестирование API клиента"""
    print("=== Тестирование API клиента ===\n")

    # Создаем клиент
    api = APIClient("http://127.0.0.1:8000")

    # Устанавливаем учетные данные
    print("Введите учетные данные для теста:")
    username = input("Имя пользователя: ").strip()
    password = input("Пароль: ").strip()

    if not username or not password:
        print("Учетные данные не введены. Выход.")
        return

    api.set_credentials(username, password)

    # Тест подключения
    print("\n1. Тест подключения...")
    try:
        if api.test_connection():
            print("✓ Подключение успешно")
        else:
            print("✗ Ошибка подключения")
            return
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return

    # Получение информации о пользователе
    print("\n2. Информация о пользователе...")
    try:
        user_info = api.get_user_info()
        print(f"✓ Пользователь: {user_info.get('username')}")
        print(f"  Email: {user_info.get('email')}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

    # Получение QSO
    print("\n3. Получение списка QSO...")
    try:
        qsos = api.get_qsos()
        print(f"✓ Получено {len(qsos)} QSO")
        if qsos:
            print(f"  Первый QSO: {qsos[0].get('callsign')} - {qsos[0].get('date')}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

    # Статистика
    print("\n4. Статистика...")
    try:
        stats = api.get_stats()
        print(f"✓ Всего QSO: {stats.get('total_qso')}")
        print(f"  Уникальных позывных: {stats.get('unique_callsigns')}")
        print(f"  Стран DXCC: {stats.get('dxcc_count')}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

    # Профиль
    print("\n5. Профиль пользователя...")
    try:
        profile = api.get_profile()
        print(f"✓ Профиль получен")
        print(f"  Позывной: {profile.get('callsign')}")
        print(f"  Локатор: {profile.get('gridsquare')}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

    # Поиск по позывному
    print("\n6. Поиск по позывному...")
    search_callsign = input("Введите часть позывного для поиска (или Enter для пропуска): ").strip()
    if search_callsign:
        try:
            results = api.search_by_callsign(search_callsign)
            print(f"✓ Найдено {len(results)} записей")
            for qso in results[:5]:  # Показываем первые 5
                print(f"  - {qso.get('callsign')} ({qso.get('date')})")
        except Exception as e:
            print(f"✗ Ошибка: {e}")

    # Поиск по QTH локатору
    print("\n7. Поиск по QTH локатору...")
    search_grid = input("Введите часть QTH локатора для поиска (или Enter для пропуска): ").strip()
    if search_grid:
        try:
            results = api.search_by_grid(search_grid)
            print(f"✓ Найдено {len(results)} записей")
            for qso in results[:5]:  # Показываем первые 5
                print(f"  - {qso.get('callsign')} ({qso.get('gridsquare')})")
        except Exception as e:
            print(f"✗ Ошибка: {e}")

    print("\n=== Тестирование завершено ===")


if __name__ == "__main__":
    test_api()
