"""
REST API клиент для взаимодействия с сервером
"""
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, List, Dict, Any
from datetime import datetime


class APIClient:
    """Клиент для работы с REST API"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.username = None
        self.password = None

    def set_credentials(self, username: str, password: str):
        """Устанавливает учетные данные для аутентификации"""
        self.username = username
        self.password = password
        self.session.auth = HTTPBasicAuth(username, password)

    def clear_credentials(self):
        """Очищает учетные данные"""
        self.username = None
        self.password = None
        self.session.auth = None

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                 data: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполняет HTTP запрос"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Ошибка авторизации. Проверьте имя пользователя и пароль.")
            elif response.status_code == 404:
                raise Exception("Ресурс не найден.")
            else:
                raise Exception(f"HTTP ошибка: {e}")
        except requests.exceptions.ConnectionError:
            raise Exception("Не удалось подключиться к серверу. Проверьте URL.")
        except requests.exceptions.Timeout:
            raise Exception("Таймаут соединения.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса: {e}")
        except ValueError:
            raise Exception("Ошибка декодирования ответа сервера.")

    # ===== QSO методы =====

    def get_qsos(self, updated_since: Optional[str] = None) -> List[Dict]:
        """Получить список всех QSO

        Args:
            updated_since: Фильтр по дате обновления (ISO формат). Если указан,
                          возвращаются только QSO, обновлённые после этой даты.
        """
        all_qsos = []
        url = '/api/v1/qsos/'
        params = {}
        if updated_since:
            params['updated_since'] = updated_since

        while url:
            result = self._request('GET', url, params=params)
            params = {}  # Сбрасываем параметры после первого запроса

            if isinstance(result, dict) and 'results' in result:
                all_qsos.extend(result['results'])
                url = result.get('next')
                if url:
                    # Преобразуем полный URL в относительный путь
                    if url.startswith('http'):
                        url = url.replace(self.base_url, '')
            else:
                all_qsos.extend(result if isinstance(result, list) else [])
                break

        return all_qsos

    def get_qso(self, qso_id: str) -> Dict:
        """Получить конкретное QSO по ID"""
        return self._request('GET', f'/api/v1/qsos/{qso_id}/')

    def create_qso(self, qso_data: Dict) -> Dict:
        """Создать новое QSO"""
        return self._request('POST', '/api/v1/qsos/', data=qso_data)

    def update_qso(self, qso_id: str, qso_data: Dict) -> Dict:
        """Обновить QSO (полностью)"""
        return self._request('PUT', f'/api/v1/qsos/{qso_id}/', data=qso_data)

    def partial_update_qso(self, qso_id: str, qso_data: Dict) -> Dict:
        """Частично обновить QSO"""
        return self._request('PATCH', f'/api/v1/qsos/{qso_id}/', data=qso_data)

    def delete_qso(self, qso_id: str) -> bool:
        """Удалить QSO"""
        self._request('DELETE', f'/api/v1/qsos/{qso_id}/')
        return True

    def get_stats(self) -> Dict:
        """Получить статистику QSO"""
        return self._request('GET', '/api/v1/qsos/stats/')

    def search_by_callsign(self, callsign: str) -> List[Dict]:
        """Поиск QSO по части позывного"""
        result = self._request('GET', '/api/v1/qsos/search/', params={'callsign': callsign})
        if isinstance(result, dict) and 'results' in result:
            return result['results']
        return result if isinstance(result, list) else []

    def search_by_band(self, band: str) -> List[Dict]:
        """Поиск QSO по диапазону"""
        result = self._request('GET', '/api/v1/qsos/by_band/', params={'band': band})
        if isinstance(result, dict) and 'results' in result:
            return result['results']
        return result if isinstance(result, list) else []

    def search_by_grid(self, grid: str) -> List[Dict]:
        """Поиск QSO по QTH локатору"""
        result = self._request('GET', '/api/v1/qsos/by_grid/', params={'grid': grid})
        if isinstance(result, dict) and 'results' in result:
            return result['results']
        return result if isinstance(result, list) else []

    def get_lotw_qsos(self) -> List[Dict]:
        """Получить QSO подтверждённые через LoTW"""
        result = self._request('GET', '/api/v1/qsos/by_lotw/')
        if isinstance(result, dict) and 'results' in result:
            return result['results']
        return result if isinstance(result, list) else []

    # ===== Profile методы =====

    def get_profile(self) -> Dict:
        """Получить профиль пользователя"""
        return self._request('GET', '/api/v1/profile/')

    def update_profile(self, profile_data: Dict) -> Dict:
        """Обновить профиль пользователя"""
        return self._request('PATCH', '/api/v1/profile/', data=profile_data)

    # ===== User Info методы =====

    def get_user_info(self) -> Dict:
        """Получить информацию о пользователе"""
        return self._request('GET', '/api/v1/user-info/')

    # ===== Тест подключения =====

    def test_connection(self) -> bool:
        """Проверка подключения к серверу"""
        try:
            # Пробуем получить информацию о пользователе
            self.get_user_info()
            return True
        except Exception:
            return False
