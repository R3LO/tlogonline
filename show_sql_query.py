#!/usr/bin/env python
"""Скрипт для демонстрации SQL запроса для подсчёта QTH локаторов"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection
from django.db.models.functions import Substr
from tlog.models import QSO
from django.contrib.auth.models import User

# Получаем тестового пользователя (первого в базе)
user = User.objects.first()

if not user:
    print("Нет пользователей в базе данных!")
    exit(1)

print(f"Используем пользователя: {user.username}\n")

# Формируем QuerySet как в lotw_qth_locators_api
lotw_qso = QSO.objects.filter(
    user=user,
    lotw='Y',
    app_lotw_rxqsl__isnull=False
)

# Применяем annotate для получения первых 4 символов локатора
lotw_qso = lotw_qso.annotate(
    locator4=Substr('gridsquare', 1, 4)
)

# Фильтруем и выбираем уникальные значения
qso_filtered = lotw_qso.filter(
    locator4__isnull=False
).exclude(locator4='').values('my_callsign', 'locator4', 'callsign').distinct()

# Показываем SQL запрос
print("=" * 80)
print("SQL ЗАПРОС Django ORM:")
print("=" * 80)
print(qso_filtered.query)
print("=" * 80)

# Также покажем упрощённую версию без фильтров
print("\nУпрощённый SQL (без фильтров по пользователю и LoTW):")
print("=" * 80)
simple_qso = QSO.objects.annotate(
    locator4=Substr('gridsquare', 1, 4)
).filter(
    locator4__isnull=False
).exclude(locator4='').values('my_callsign', 'locator4', 'callsign').distinct()

print(simple_qso.query)
print("=" * 80)

# Показываем объяснение того, что делает запрос
print("\nПОЯСНЕНИЕ:")
print("=" * 80)
print("1. SUBSTR(tlog_qso.gridsquare, 1, 4) - берёт первые 4 символа из gridsquare")
print("2. FILTER по пользователю, lotw='Y' и app_lotw_rxqsl__isnull=False")
print("3. DISTINCT - уникальные комбинации (my_callsign, locator4, callsign)")
print("=" * 80)
