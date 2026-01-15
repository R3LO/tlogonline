#!/usr/bin/env python
"""
Детальная диагностика парсера ADIF
"""

import os
import sys
import django

# Настройка Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.views import parse_adif_record, process_adif_file
from frontend.models import QSO
from django.contrib.auth.models import User

def debug_adif_parsing():
    """Детальная диагностика парсинга ADIF"""
    
    user = User.objects.first()
    if not user:
        print("[ERROR] Пользователи не найдены")
        return
        
    print(f"=== Детальная диагностика парсинга для пользователя: {user.username} ===")
    
    # Тестовая запись
    test_record = """<BAND:4>13cm <CALL:6>GM0MUW <CONT:2>EU <CONTEST_ID:6>QO-100 <CQZ:2>14 <MY_GRIDSQUARE:6>KO55ve <DXCC:3>279 <FREQ:12>10489.899880 <ITUZ:2>27 <MODE:3>SSB <OPERATOR:6>R3LO/P <PFX:3>GM0 <PROP_MODE:3>SAT <QSO_DATE:8>20260103 <TIME_ON:6>111949 <RST_RCVD:3>599 <RST_SENT:3>599 <SAT_NAME:6>QO-100 <STX:1>1 <TIME_OFF:6>111949 <APP_LOGGER32_QSO_NUMBER:4>5659 <FREQ_RX:12>10489.899880 <EOR>"""
    
    print("=== Тестирование парсера ===")
    print(f"Исходная запись: {test_record}")
    print()
    
    try:
        result = parse_adif_record(test_record)
        
        if result:
            print("[OK] Парсинг успешен")
            print("Распарсенные данные:")
            for key, value in result.items():
                print(f"  {key}: {type(value).__name__} = {repr(value)}")
            print()
            
            # Проверяем обязательные поля
            required_fields = ['callsign', 'date', 'time']
            missing_fields = []
            for field in required_fields:
                if field not in result:
                    missing_fields.append(field)
                elif result[field] is None:
                    missing_fields.append(f"{field} (None)")
                elif field == 'callsign' and not result[field]:
                    missing_fields.append(f"{field} (пустая строка)")
                    
            if missing_fields:
                print(f"[ERROR] Отсутствуют обязательные поля: {missing_fields}")
            else:
                print("[OK] Все обязательные поля присутствуют")
                
            # Проверяем частоту
            if 'frequency' in result:
                freq = result['frequency']
                print(f"Частота: {freq} (тип: {type(freq)})")
                if isinstance(freq, (int, float)) and freq > 0:
                    print("[OK] Частота валидна")
                else:
                    print("[WARNING] Частота проблематична")
            else:
                print("[WARNING] Частота отсутствует")
                
            # Проверяем режим
            if 'mode' in result:
                mode = result['mode']
                print(f"Режим: {mode}")
                if mode in ['SSB', 'CW', 'FM', 'AM', 'RTTY', 'PSK31', 'PSK63', 'FT8', 'FT4', 'JT65', 'JT9', 'SSTV', 'JS8', 'MSK144']:
                    print("[OK] Режим валиден")
                else:
                    print(f"[WARNING] Режим '{mode}' может быть не в списке поддерживаемых")
            else:
                print("[WARNING] Режим отсутствует")
                
            # Пробуем создать QSO объект
            print("\n=== Тестирование создания QSO объекта ===")
            try:
                qso_obj = QSO(
                    user=user,
                    my_callsign="R3LO",
                    callsign=result.get('callsign', ''),
                    date=result.get('date'),
                    time=result.get('time'),
                    frequency=result.get('frequency', 0.0),
                    band=result.get('band', ''),
                    mode=result.get('mode', 'SSB'),
                    rst_sent=result.get('rst_sent', ''),
                    rst_received=result.get('rst_received', ''),
                    my_gridsquare=result.get('my_gridsquare', ''),
                    his_gridsquare=result.get('his_gridsquare', '')
                )
                
                print("[OK] QSO объект создан")
                
                # Пробуем валидацию Django
                try:
                    qso_obj.full_clean()
                    print("[OK] Django валидация пройдена")
                except Exception as validation_error:
                    print(f"[ERROR] Django валидация не пройдена: {validation_error}")
                    
                # Пробуем сохранить
                try:
                    qso_obj.save()
                    print(f"[OK] QSO объект сохранен с ID: {qso_obj.id}")
                    
                    # Удаляем тестовую запись
                    qso_obj.delete()
                    print("[OK] Тестовая запись удалена")
                    
                except Exception as save_error:
                    print(f"[ERROR] Ошибка сохранения: {save_error}")
                    
            except Exception as create_error:
                print(f"[ERROR] Ошибка создания QSO объекта: {create_error}")
                
        else:
            print("[ERROR] Парсинг не дал результатов")
            
    except Exception as e:
        print(f"[ERROR] Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_adif_parsing()