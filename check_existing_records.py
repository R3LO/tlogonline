#!/usr/bin/env python
"""
Проверка существующих записей в базе данных
"""

import os
import sys
import django

# Настройка Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.models import QSO, ADIFUpload
from django.contrib.auth.models import User

def check_existing_records():
    """Проверяем существующие записи в базе"""
    
    user = User.objects.first()
    if not user:
        print("[ERROR] Пользователи не найдены")
        return
        
    print(f"=== Проверка записей для пользователя: {user.username} ===")
    
    # Проверяем QSO записи
    qsos = QSO.objects.filter(user=user).order_by('-date', '-time')
    print(f"\nQSO записей в базе: {qsos.count()}")
    
    if qsos.exists():
        print("Последние 5 QSO записей:")
        for i, qso in enumerate(qsos[:5]):
            print(f"  {i+1}. {qso.date} {qso.time} - {qso.my_callsign} -> {qso.callsign} ({qso.band}/{qso.mode}) - {qso.frequency} MHz")
    
    # Проверяем загрузки ADIF файлов
    uploads = ADIFUpload.objects.filter(user=user).order_by('-upload_date')
    print(f"\nADIF загрузок: {uploads.count()}")
    
    if uploads.exists():
        print("Последние 5 загрузок:")
        for i, upload in enumerate(uploads[:5]):
            print(f"  {i+1}. {upload.upload_date} - {upload.filename} ({upload.qso_count} записей)")
    
    # Проверяем конкретную запись из теста
    specific_qso = QSO.objects.filter(
        user=user,
        callsign='GM0MUW',
        date='2026-01-03',
        time='11:19:49'
    )
    
    if specific_qso.exists():
        print(f"\n[OK] Найдена тестовая запись GM0MUW: {specific_qso.count()} записей")
        for qso in specific_qso:
            print(f"  ID: {qso.id}, Частота: {qso.frequency}, Режим: {qso.mode}")
    else:
        print(f"\n[INFO] Тестовая запись GM0MUW не найдена")
    
    # Удаляем тестовые записи для чистого теста
    print(f"\n=== Очистка тестовых данных ===")
    deleted_qsos = QSO.objects.filter(user=user, callsign='GM0MUW').delete()
    print(f"Удалено QSO записей: {deleted_qsos[0]}")
    
    deleted_uploads = ADIFUpload.objects.filter(user=user, filename__contains='test').delete()
    print(f"Удалено загрузок: {deleted_uploads[0]}")

if __name__ == "__main__":
    check_existing_records()