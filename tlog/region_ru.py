#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль определения региона России по позывному
Возвращает: двухбуквенный код региона и полное название
"""

import re

class RussianRegionFinder:
    """
    Определитель региона России по позывному
    Возвращает код региона (2 буквы) и полное название
    """

    def __init__(self, exceptions_file=None):
        """Инициализация с загрузкой данных и исключений"""
        self.region_data = self._load_region_data()
        self.region_codes = {name: code for code, name in self.region_data.items()}
        self.exceptions = self._load_exceptions(exceptions_file)

    def _load_region_data(self):
        """Загрузка данных о регионах"""
        return {
            'KK': 'Красноярский край',
            'HK': 'Хабаровский край',
            'EA': 'Еврейская А.О.',
            'SL': 'Сахалинская область',
            'MG': 'Магаданская область',
            'AM': 'Амурская область',
            'CK': 'Чукотский А.О.',
            'PK': 'Приморский край',
            'BU': 'Республика Бурятия',
            'YA': 'Республика Саха (Якутия)',
            'IR': 'Иркутская область',
            'ZK': 'Забайкальский край',
            'HA': 'Республика Хакасия',
            'TU': 'Республика Тыва',
            'KT': 'Камчатский край',
            'SP': 'г. Санкт-Петербург',
            'LO': 'Ленинградская область',
            'HE': 'Херсонская область',
            'KL': 'Республика Карелия',
            'AR': 'Архангельская область',
            'NO': 'Ненецкий А.О.',
            'VO': 'Вологодская область',
            'NV': 'Новгородская область',
            'PS': 'Псковская область',
            'KO': 'Республика Коми',
            'MU': 'Мурманская область',
            'KA': 'Калининградская область',
            'MA': 'г. Москва',
            'MO': 'Московская область',
            'OR': 'Орловская область',
            'LP': 'Липецкая область',
            'TV': 'Тверская область',
            'SM': 'Смоленская область',
            'YR': 'Ярославская область',
            'KS': 'Костромская область',
            'TL': 'Тульская область',
            'VR': 'Воронежская область',
            'TB': 'Тамбовская область',
            'RA': 'Рязанская область',
            'NN': 'Нижегородская область',
            'IV': 'Ивановская область',
            'VL': 'Владимирская область',
            'KU': 'Курская область',
            'KG': 'Калужская область',
            'BR': 'Брянская область',
            'BO': 'Белгородская область',
            'VG': 'Волгоградская область',
            'SA': 'Саратовская область',
            'PE': 'Пензенская область',
            'SR': 'Самарская область',
            'UL': 'Ульяновская область',
            'KI': 'Кировская область',
            'TA': 'Республика Татарстан',
            'MR': 'Республика Марий Эл',
            'MD': 'Республика Мордовия',
            'UD': 'Удмуртская Республика',
            'CU': 'Чувашская Республика',
            'KR': 'Краснодарский край',
            'KC': 'Карачаево-Черкесская Республика',
            'ST': 'Ставропольский край',
            'KM': 'Республика Калмыкия',
            'SO': 'Республика Северная Осетия - Алания',
            'RK': 'Республика Крым',
            'RO': 'Ростовская область',
            'DO': 'Донецкая Народная Республика',
            'CN': 'Чеченская Республика',
            'IN': 'Республика Ингушетия',
            'SE': 'г. Севастополь',
            'ZP': 'Запорожская область',
            'AO': 'Астраханская область',
            'DA': 'Республика Дагестан',
            'KB': 'Кабардино-Балкарская Республика',
            'AD': 'Республика Адыгея',
            'LU': 'Луганская Народная Республика',
            'CB': 'Челябинская область',
            'SV': 'Свердловская область',
            'PM': 'Пермский край',
            'TO': 'Томская область',
            'HM': 'Ханты-Мансийский А.О. - Югра',
            'YN': 'Ямало-Ненецкий А.О.',
            'TN': 'Тюменская область',
            'OM': 'Омская область',
            'NS': 'Новосибирская область',
            'KN': 'Курганская область',
            'OB': 'Оренбургская область',
            'KE': 'Кемеровская область',
            'BA': 'Республика Башкортостан',
            'AL': 'Алтайский край',
            'GA': 'Республика Алтай'
        }

    def _load_exceptions(self, exceptions_file):
        """Загрузка исключений из файла"""
        exceptions = {}

        if exceptions_file:
            try:
                with open(exceptions_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split(':')
                            if len(parts) >= 2:
                                callsign = parts[0].strip().upper()
                                region_code = parts[1].strip().upper()
                                exceptions[callsign] = region_code
            except FileNotFoundError:
                print(f"Файл исключений {exceptions_file} не найден")

        return exceptions

    def add_exception(self, callsign, region_code):
        """Добавление исключения"""
        self.exceptions[callsign.upper()] = region_code.upper()

    def find_region(self, callsign):
        """
        Определение региона по позывному

        Args:
            callsign (str): Позывной для проверки

        Returns:
            dict: Словарь с кодом региона и названием, или None если не найден
            {
                'code': 'SM',          # двухбуквенный код
                'name': 'Смоленская область',  # полное название
                'callsign': 'R3LO'     # исходный позывной
            }
        """
        callsign = callsign.upper().strip()

        # 1. Проверка исключений
        if callsign in self.exceptions:
            region_code = self.exceptions[callsign]
            if region_code in self.region_data:
                return {
                    'code': region_code,
                    'name': self.region_data[region_code],
                    'callsign': callsign
                }

        # 2. Определение по общему правилу (цифра + следующая буква)
        zone, letter = self._extract_zone_and_letter(callsign)

        if zone and letter:
            region_code = self._get_region_code(zone, letter)
            if region_code and region_code in self.region_data:
                return {
                    'code': region_code,
                    'name': self.region_data[region_code],
                    'callsign': callsign
                }

        # 3. Регион не найден
        return None

    def get_region_info(self, callsign):
        """
        Получение информации о регионе (удобный интерфейс)

        Returns:
            tuple: (код_региона, название_региона) или (None, None)
        """
        result = self.find_region(callsign)
        if result:
            return result['code'], result['name']
        return None, None

    def get_region_code(self, callsign):
        """Получение только кода региона"""
        try:
            result = self.find_region(callsign)
            if result and result.get('code'):
                return result['code']
            return None
        except (TypeError, KeyError):
            return None

    def get_region_name(self, callsign):
        """Получение только названия региона"""
        try:
            result = self.find_region(callsign)
            if result and result.get('name'):
                return result['name']
            return None
        except (TypeError, KeyError):
            return None

    def _extract_zone_and_letter(self, callsign):
        """Извлечение цифры и буквы после неё"""
        # Паттерн: буква-цифра-буква
        match = re.search(r'[A-Z](\d)([A-Z])', callsign)
        if match:
            return match.group(1), match.group(2)

        # Для формата R3
        if len(callsign) >= 2 and callsign[0] == 'R' and callsign[1].isdigit():
            zone = callsign[1]
            if len(callsign) >= 3 and callsign[2].isalpha():
                return zone, callsign[2]

        return None, None

    def _get_region_code(self, zone, letter):
        """Получение кода региона по цифре и букве"""
        mapping = {
            '0': {'A':'KK','B':'KK','H':'KK','C':'HK','D':'EA','E':'SL','F':'SL',
                  'I':'MG','J':'AM','K':'CK','L':'PK','M':'PK','N':'PK','O':'BU',
                  'Q':'YA','S':'IR','T':'IR','U':'ZK','V':'ZK','W':'HA','X':'KT',
                  'Z':'KT','Y':'TU'},
            '1': {'A':'SP','B':'SP','D':'SP','F':'SP','G':'SP','J':'SP','L':'SP','M':'SP',
                  'C':'LO','H':'HE','V':'HE','I':'KO','N':'KL','O':'AR','P':'NO',
                  'Q':'VO','R':'VO','S':'VO','T':'NV','W':'PS','Z':'MU'},
            '2': {'A':'MA','B':'MA','C':'MA','D':'MO','H':'MO','E':'OR','F':'KA',
                  'K':'KA','G':'LP','I':'TV','L':'SM','M':'YR','N':'KS','O':'VR',
                  'Q':'VR','P':'TL','R':'TB','S':'RA','T':'NN','U':'IV','V':'VL',
                  'W':'KU','X':'KG','Y':'BR','Z':'BO'},
            '3': {'A':'MA','D':'MA','O':'MA','W':'MA','B':'MO','C':'MO','F':'MO',
                  'H':'MO','J':'MO','M':'MO','E':'OR','G':'LP','I':'TV','K':'VR',
                  'Q':'VR','L':'SM','N':'KS','P':'TL','R':'TB','S':'RA','T':'NN',
                  'U':'IV','V':'VL','X':'KG','Y':'BR','Z':'BO'},
            '4': {'A':'VG','B':'VG','C':'SA','D':'SA','F':'PE','H':'SR','I':'SR',
                  'L':'UL','M':'UL','N':'KI','O':'KI','P':'TA','Q':'TA','R':'TA',
                  'S':'MR','T':'MR','U':'MD','W':'UD','Y':'CU','Z':'CU'},
            '6': {'A':'KR','B':'KR','C':'KR','D':'KR','E':'KC','F':'ST','G':'ST',
                  'H':'ST','T':'ST','I':'KM','J':'SO','K':'RK','L':'RO','M':'RO',
                  'N':'RO','O':'DO','P':'CN','Q':'IN','R':'SE','S':'ZP','U':'AO',
                  'V':'AO','W':'DA','X':'KB','Y':'AD','Z':'LU'},
            '9': {'A':'CB','B':'CB','C':'SV','D':'SV','E':'SV','F':'PM','G':'PM',
                  'H':'TO','I':'TO','J':'HM','K':'YN','L':'TN','M':'OM','N':'OM',
                  'O':'NS','P':'NS','Q':'KN','R':'KN','S':'OB','T':'OB','U':'KE',
                  'V':'KE','W':'BA','X':'KO','Y':'AL','Z':'GA'},
            '8': {'A':'CB','B':'CB','C':'SV','D':'SV','E':'SV','F':'PM','G':'PM',
                  'H':'TO','I':'TO','J':'HM','K':'YN','L':'TN','M':'OM','N':'OM',
                  'O':'NS','P':'NS','Q':'KN','R':'KN','S':'OB','T':'OB','U':'KE',
                  'V':'KE','W':'BA','X':'KO','Y':'AL'},
        }

        if zone in mapping and letter in mapping[zone]:
            return mapping[zone][letter]

        return None

    def get_all_regions(self):
        """Получение списка всех регионов с кодами"""
        return [(code, name) for code, name in self.region_data.items()]

    def search_region_by_name(self, search_text):
        """Поиск региона по названию"""
        search_text = search_text.lower()
        results = []

        for code, name in self.region_data.items():
            if search_text in name.lower():
                results.append((code, name))

        return results

    def search_region_by_code(self, search_code):
        """Поиск региона по коду"""
        search_code = search_code.upper()
        if search_code in self.region_data:
            return [(search_code, self.region_data[search_code])]
        return []




if __name__ == "__main__":
    finder = RussianRegionFinder('exceptions.dat')
    callsign = "Rf2cfO"
    full_info = finder.find_region(callsign)
    print(f'{full_info}')
