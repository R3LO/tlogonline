#!/usr/bin/env python
"""Миграция для нормализации регистра поля band в нижний регистр"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from tlog.models import QSO
from django.db.models.functions import Lower

def migrate_band():
    # Проверяем текущее состояние
    bands_before = QSO.objects.exclude(band__isnull=True).exclude(band='').values_list('band', flat=True).distinct()
    print('До миграции:', list(bands_before))
    
    # Обновляем band на нижний регистр
    updated = QSO.objects.filter(band__isnull=False).exclude(band='').update(band=Lower('band'))
    print(f'Обновлено записей: {updated}')
    
    # Проверяем результат
    bands_after = QSO.objects.exclude(band__isnull=True).exclude(band='').values_list('band', flat=True).distinct()
    print('После миграции:', list(bands_after))

if __name__ == '__main__':
    migrate_band()