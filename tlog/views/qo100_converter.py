# Конвертер ADIF файлов QO-100

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from ..models import check_user_blocked
import os
import uuid
import re


@login_required
def qo100_converter(request):
    """
    Конвертер ADIF файлов для QO-100
    """
    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    preview = None
    download_url = None
    download_filename = None

    if request.method == 'POST':
        try:
            adif_file = request.FILES.get('adif_file')
            if not adif_file:
                messages.error(request, 'Пожалуйста, выберите файл для загрузки')
                return render(request, 'qo100/converter.html')

            # Читаем содержимое файла
            content = adif_file.read().decode('utf-8', errors='ignore')

            # Переводим в верхний регистр для统一 обработки
            content = content.upper()

            # Проверяем наличие обязательного тега EOH
            if 'EOH' not in content:
                messages.error(request, 'Некорректный ADIF файл: отсутствует тег EOH')
                return render(request, 'qo100/converter.html')

            # Обрабатываем файл
            result = process_adif_content(content)
            
            if result['error']:
                messages.error(request, result['error'])
                return render(request, 'qo100/converter.html')

            preview = result['preview']
            
            # Если есть данные для скачивания
            if result['download_content']:
                # Сохраняем файл во временную папку
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                
                download_filename = f"qo100_converted_{uuid.uuid4().hex[:8]}.adi"
                download_path = os.path.join(temp_dir, download_filename)
                
                with open(download_path, 'w', encoding='utf-8') as f:
                    f.write(result['download_content'])
                
                download_url = f"/media/temp/{download_filename}"

            messages.success(request, f'Файл успешно обработан. Найдено QSO: {result["qso_count"]}')

        except Exception as e:
            messages.error(request, f'Ошибка при обработке файла: {str(e)}')

    return render(request, 'qo100/converter.html', {
        'preview': preview,
        'download_url': download_url,
        'download_filename': download_filename,
    })


def process_adif_content(content):
    """
    Обработка содержимого ADIF файла
    """
    try:
        # Разделяем на заголовок и данные
        eoh_pos = content.find('EOH')
        if eoh_pos == -1:
            return {'error': 'Некорректный ADIF файл: отсутствует тег EOH'}
        
        header = content[:eoh_pos + 3]
        data = content[eoh_pos + 3:]
        
        # Извлекаем информацию о полях из заголовка
        fields_info = parse_adif_header(header)
        
        # Парсим записи QSO
        qso_records = parse_adif_records(data, fields_info)
        
        if not qso_records:
            return {'error': 'В файле не найдено записей QSO'}
        
        # Фильтруем и обрабатываем записи для QO-100
        processed_qso = []
        download_content = []
        
        for record in qso_records:
            # Проверяем, что QSO относится к QO-100
            if is_qo100_qso(record):
                processed_record = process_qso_record(record)
                if processed_record:
                    processed_qso.append(processed_record)
                    # Добавляем в содержимое для скачивания
                    download_content.append(format_qso_for_download(processed_record))
        
        if not processed_qso:
            return {'error': 'В файле не найдено QSO, связанных с QO-100'}
        
        # Формируем превью (первые 10 записей)
        preview = processed_qso[:10]
        
        # Формируем содержимое для скачивания
        download_text = '\n'.join(download_content)
        
        return {
            'preview': preview,
            'download_content': download_text,
            'qso_count': len(processed_qso)
        }
        
    except Exception as e:
        return {'error': f'Ошибка при обработке файла: {str(e)}'}


def parse_adif_header(header):
    """
    Парсинг заголовка ADIF файла
    """
    fields_info = {}
    
    # Ищем определения полей в формате <FIELDn:len:fieldname>
    field_pattern = r'<FIELD(\d+):(\d+):([^:]+)>'
    matches = re.findall(field_pattern, header)
    
    for field_num, field_len, field_name in matches:
        fields_info[field_name.upper()] = int(field_num)
    
    return fields_info


def parse_adif_records(data, fields_info):
    """
    Парсинг записей QSO из ADIF данных
    """
    records = []
    
    # Разделяем записи по символу <EOR>
    record_strings = data.split('<EOR>')
    
    for record_string in record_strings:
        record_string = record_string.strip()
        if not record_string:
            continue
            
        record = {}
        
        # Парсим каждое поле в записи
        field_pattern = r'<([A-Z_]+):(\d+):?([A-Z_]*)?>([^<]*)'
        matches = re.findall(field_pattern, record_string)
        
        for field_name, field_len, field_type, field_value in matches:
            field_name = field_name.upper()
            field_value = field_value.strip()
            
            # Преобразуем типы данных если указано
            if field_type == 'D':
                # Дата в формате YYYYMMDD
                if len(field_value) == 8:
                    field_value = f"{field_value[:4]}-{field_value[4:6]}-{field_value[6:8]}"
            elif field_type == 'T':
                # Время в формате HHMMSS
                if len(field_value) == 6:
                    field_value = f"{field_value[:2]}:{field_value[2:4]}:{field_value[4:6]}"
            
            record[field_name] = field_value
        
        if record:
            records.append(record)
    
    return records


def is_qo100_qso(record):
    """
    Проверка, относится ли QSO к QO-100
    """
    # Проверяем диапазон частот QO-100 (10 GHz)
    freq = record.get('FREQ', '')
    band = record.get('BAND', '')
    
    # QO-100 работает на частотах около 10 GHz
    qo100_bands = ['10GHZ', '10', '10G', '10GH']
    qo100_freqs = ['10489', '10490', '10491', '10492', '10493', '10494', '10495']
    
    if band in qo100_bands:
        return True
    
    if any(freq_start in freq for freq_start in qo100_freqs):
        return True
    
    # Проверяем спутник
    sat_name = record.get('SAT_NAME', '').upper()
    if 'QO' in sat_name or 'OSCAR' in sat_name:
        return True
    
    # Проверяем режим распространения
    prop_mode = record.get('PROP_MODE', '').upper()
    if prop_mode == 'SAT':
        sat_name = record.get('SAT_NAME', '').upper()
        if 'QO' in sat_name:
            return True
    
    return False


def process_qso_record(record):
    """
    Обработка записи QSO для QO-100
    """
    try:
        processed = {}
        
        # Основные поля
        processed['callsign'] = record.get('CALL', '').upper()
        processed['date'] = record.get('QSO_DATE', '')
        processed['time'] = record.get('TIME_ON', '')
        processed['mode'] = record.get('MODE', '').upper()
        processed['band'] = record.get('BAND', '').upper()
        processed['freq'] = record.get('FREQ', '')
        
        # Дополнительные поля
        processed['rst_rcvd'] = record.get('RST_RCVD', '')
        processed['rst_sent'] = record.get('RST_SENT', '')
        processed['gridsquare'] = record.get('GRIDSQUARE', '').upper()
        processed['qth'] = record.get('QTH', '')
        processed['name'] = record.get('NAME', '')
        
        # Информация о спутнике
        processed['sat_name'] = record.get('SAT_NAME', '').upper()
        processed['prop_mode'] = record.get('PROP_MODE', '').upper()
        
        # Проверяем обязательные поля
        if not all([processed['callsign'], processed['date'], processed['time'], processed['mode']]):
            return None
        
        return processed
        
    except Exception:
        return None


def format_qso_for_download(record):
    """
    Форматирование записи QSO для скачивания
    """
    lines = []
    
    # Форматируем поля для ADIF
    for field, value in record.items():
        if value:
            if field in ['date']:
                # Дата в формате YYYYMMDD
                date_value = value.replace('-', '')
                lines.append(f"<{field}:8>{date_value}")
            elif field in ['time']:
                # Время в формате HHMMSS
                time_value = value.replace(':', '').replace('-', '')
                lines.append(f"<{field}:6>{time_value}")
            else:
                lines.append(f"<{field}:{len(value)}>{value}")
    
    lines.append("<EOR>")
    return '\n'.join(lines)


def qo100_converter_download(request):
    """
    Скачивание конвертированного файла
    """
    import os
    from django.conf import settings
    from django.http import HttpResponse
    from django.contrib import messages
    from django.shortcuts import redirect

    if not request.user.is_authenticated:
        return redirect('login_page')

    # Получаем параметр filename из URL
    filename = request.GET.get('filename', '')
    if not filename:
        messages.error(request, 'Файл не найден')
        return redirect('qo100_converter')

    # Проверяем безопасность пути
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.MEDIA_ROOT, 'temp', safe_filename)

    # Проверяем существование файла
    if not os.path.exists(file_path):
        messages.error(request, 'Файл не найден или срок хранения истёк')
        return redirect('qo100_converter')

    # Отдаем файл
    with open(file_path, 'rb') as f:
        content = f.read()

    response = HttpResponse(content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
    return response