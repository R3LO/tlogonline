#!/usr/bin/env python
import sys
sys.path.insert(0, 'E:/Project_TlogDjango')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tlog.settings')
import django
django.setup()

from tlog.region_ru import RussianRegionFinder

# Тест без файла исключений
print("=== Тест без файла исключений ===")
f1 = RussianRegionFinder()
print('R3LA:', f1.get_region_code('R3LA'))
print('UA1AB:', f1.get_region_code('UA1AB'))

# Тест с файлом исключений
print("\n=== Тест с файлом исключений ===")
f2 = RussianRegionFinder('E:/Project_TlogDjango/tlog/exceptions.dat')
print('R3LA:', f2.get_region_code('R3LA'))
print('UA1AB:', f2.get_region_code('UA1AB'))
print('R3LO:', f2.get_region_code('R3LO'))  # Из исключений

print("\n=== Тест импорта views ===")
from tlog.views.logbook import add_qso
from tlog.views.adif import process_adif_file
print("Импорт успешен!")

print("\nВсе тесты пройдены!")