#!/usr/bin/env python3
"""
Удаление информации о спутниках из примечаний QSO
"""
import os
import sys
import django
import re

# Настройка Django
sys.path.append('/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.models import QSO

def remove_satellite_info():
    """Убираем информацию о спутниках из примечаний"""

    # Находим записи с примечаниями о спутниках
    qso_list = QSO.objects.filter(notes__icontains='Satellite:')

    print(f"Найдено QSO с примечаниями о спутниках: {qso_list.count()}")

    # Обновляем каждую запись
    updated_count = 0
    for qso in qso_list:
        original_notes = qso.notes
        new_notes = original_notes

        # Удаляем различные варианты записи спутника
        # Убираем полностью "Satellite: QO-100" с возможными разделителями
        new_notes = re.sub(r'\s*\|\s*Satellite: QO-100\s*', '', new_notes)
        new_notes = re.sub(r'Satellite: QO-100\s*', '', new_notes)
        new_notes = re.sub(r'\s*Satellite: QO-100\s*', '', new_notes)

        # Убираем лишние разделители в конце и начале
        new_notes = re.sub(r'\s*\|\s*$', '', new_notes)
        new_notes = new_notes.strip()

        # Если после удаления остались только разделители, убираем их
        if new_notes == '|':
            new_notes = ''

        if new_notes != original_notes:
            qso.notes = new_notes
            qso.save()
            updated_count += 1
            print(f"Обновлен {qso.callsign}: '{original_notes[:50]}...' -> '{new_notes[:50]}...'")

    print(f"\nОбновлено {updated_count} записей")

    # Проверяем результат
    remaining_count = QSO.objects.filter(notes__icontains='Satellite:').count()
    print(f"Осталось записей с примечаниями о спутниках: {remaining_count}")

if __name__ == '__main__':
    remove_satellite_info()