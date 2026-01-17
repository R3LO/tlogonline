"""
Представления для загрузки и обработки ADIF файлов
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from ..models import QSO, ADIFUpload
import os
import uuid
import re
from datetime import date, time
from django.db import transaction


def adif_upload(request):
    """
    Обработка загрузки ADIF файла через обычную форму
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    if request.method == 'POST':
        try:
            # Проверяем наличие файла
            if 'file' not in request.FILES:
                messages.error(request, 'Файл не выбран')
                return redirect('dashboard')

            from ..models import ADIFUpload

            uploaded_file = request.FILES['file']

            # Проверяем расширение файла
            if not uploaded_file.name.lower().endswith(('.adi', '.adif')):
                messages.error(request, 'Неподдерживаемый формат файла. Разрешены только .adi и .adif файлы')
                return redirect('dashboard')

            # Проверяем размер файла (максимум 10MB)
            if uploaded_file.size > 10 * 1024 * 1024:
                messages.error(request, 'Размер файла превышает 10MB')
                return redirect('dashboard')

            # Создаем запись в базе данных
            adif_upload = ADIFUpload.objects.create(
                user=request.user,
                file_name=uploaded_file.name,
                file_size=uploaded_file.size,
                processed=False
            )

            # Сохраняем файл
            file_extension = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"adif/{unique_filename}"

            # Создаем директорию если не существует
            full_dir = os.path.join(default_storage.location, 'adif')
            os.makedirs(full_dir, exist_ok=True)

            # Сохраняем файл
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))

            # Запускаем обработку файла
            try:
                qso_count = process_adif_file(saved_path, request.user, adif_upload.id)

                adif_upload.processed = True
                adif_upload.qso_count = qso_count
                adif_upload.save()

                messages.success(request, f'Файл "{uploaded_file.name}" успешно загружен и обработан. Добавлено {qso_count} записей QSO.')

            except Exception as process_error:
                adif_upload.processed = True
                adif_upload.error_message = f'Ошибка обработки: {str(process_error)}'
                adif_upload.save()

                messages.warning(request, f'Файл "{uploaded_file.name}" загружен, но произошла ошибка при обработке: {str(process_error)}')

        except Exception as e:
            messages.error(request, f'Ошибка при загрузке файла: {str(e)}')

    return redirect('dashboard')


def process_adif_file(file_path, user, adif_upload_id=None):
    """
    Обрабатывает ADIF файл и создает записи QSO

    Args:
        file_path: Путь к файлу
        user: Пользователь
        adif_upload_id: ID записи ADIFUpload для связи с QSO
    """
    # Получаем полный путь к файлу
    media_root = default_storage.location
    clean_path = file_path.replace('media/', '').replace('media\\', '')
    full_path = os.path.join(media_root, clean_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Файл не найден: {full_path}")

    with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()

    # Парсер ADIF - извлекаем записи QSO
    qso_records = []
    lines = content.split('\n')
    in_qso_section = False
    current_record = []

    for line in lines:
        line = line.strip()

        # Пропускаем заголовки до <EOH>
        if line == '<EOH>' or line == '<eoh>':
            in_qso_section = True
            continue

        # Если в файле нет явного <EOH>, начинаем обработку после первой строки с позывным
        if not in_qso_section and '<call:' in line:
            in_qso_section = True

        # Обрабатываем записи QSO
        if in_qso_section and line:
            if line.startswith('<'):
                if current_record:
                    full_record = ' '.join(current_record).replace('  ', ' ')
                    if full_record.strip():
                        qso_records.append(full_record.strip())
                    current_record = []
                current_record.append(line)
            else:
                if current_record:
                    current_record.append(line)

    # Добавляем последнюю запись
    if current_record:
        full_record = ' '.join(current_record).replace('  ', ' ')
        if full_record.strip():
            qso_records.append(full_record.strip())

    # Получаем позывной пользователя из профиля
    try:
        user_callsign = user.radio_profile.callsign
        if not user_callsign:
            user_callsign = user.username
    except:
        user_callsign = user.username

    # Пакетная обработка
    batch_size = 100
    qso_count = 0
    skipped_count = 0
    error_count = 0

    for i in range(0, len(qso_records), batch_size):
        batch = qso_records[i:i + batch_size]
        qso_objects = []

        for record in batch:
            try:
                qso_data = parse_adif_record(record)
                if qso_data:
                    duplicate_check = QSO.objects.filter(
                        user=user,
                        my_callsign=user_callsign,
                        callsign=qso_data.get('callsign', ''),
                        date=qso_data.get('date'),
                        time=qso_data.get('time'),
                        band=qso_data.get('band', ''),
                        mode=qso_data.get('mode', 'SSB')
                    ).exists()

                    if not duplicate_check:
                        # Валидация и очистка данных
                        frequency = qso_data.get('frequency', 0.0)
                        if not isinstance(frequency, (int, float)) or frequency < 0:
                            frequency = 0.0

                        callsign = qso_data.get('callsign', '').strip()[:20]
                        my_callsign = user_callsign.strip()[:20]
                        band = qso_data.get('band', '').strip()[:10]
                        mode = qso_data.get('mode', 'SSB')
                        rst_sent = qso_data.get('rst_sent', '').strip()[:10]
                        rst_rcvd = qso_data.get('rst_rcvd', '').strip()[:10]
                        my_gridsquare = qso_data.get('my_gridsquare', '').strip()[:10]
                        his_gridsquare = qso_data.get('his_gridsquare', '').strip()[:10]

                        if not callsign:
                            skipped_count += 1
                            continue

                        qso_obj = QSO(
                            user=user,
                            my_callsign=my_callsign,
                            callsign=callsign,
                            date=qso_data.get('date'),
                            time=qso_data.get('time'),
                            frequency=frequency,
                            band=band,
                            mode=mode,
                            rst_sent=rst_sent,
                            rst_rcvd=rst_rcvd,
                            my_gridsquare=my_gridsquare,
                            his_gridsquare=his_gridsquare,
                            lotw_qsl='N',
                            paper_qsl='N',
                            adif_upload_id=adif_upload_id
                        )

                        if not qso_obj.callsign or not qso_obj.date or not qso_obj.time:
                            skipped_count += 1
                            continue
                        qso_objects.append(qso_obj)
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
            except Exception:
                error_count += 1
                continue

        # Пакетная вставка
        if qso_objects:
            try:
                with transaction.atomic():
                    QSO.objects.bulk_create(qso_objects, batch_size=50)
                    qso_count += len(qso_objects)
            except Exception:
                error_count += len(qso_objects)

    return qso_count


def parse_adif_record(record):
    """
    Парсит одну запись ADIF
    """
    data = {}

    # Паттерны для извлечения полей ADIF
    patterns = {
        'callsign': r'<call:(\d+)>([^<]+)',
        'name': r'<name:(\d+)>([^<]+)',
        'qth': r'<qth:(\d+)>([^<]+)',
        'location': r'<location:(\d+)>([^<]+)',
        'mode': r'<mode:(\d+)>([^<]+)',
        'band': r'<band:(\d+)>([^<]+)',
        'freq': r'<freq:(\d+)>([^<]+)',
        'freq_rx': r'<freq_rx:(\d+)>([^<]+)',
        'band_rx': r'<band_rx:(\d+)>([^<]+)',
        'qso_date': r'<qso_date:(\d+)>(\d{8})',
        'time_on': r'<time_on:(\d+)>(\d{4,6})',
        'qso_date_off': r'<qso_date_off:(\d+)>(\d{8})',
        'time_off': r'<time_off:(\d+)>(\d{4,6})',
        'rst_sent': r'<rst_sent:(\d+)>([^<]+)',
        'rst_rcvd': r'<rst_rcvd:(\d+)>([^<]+)',
        'signal_report': r'<signal_report:(\d+)>([^<]+)',
        'notes': r'<notes:(\d+)>([^<]+)',
        'gridsquare': r'<gridsquare:(\d+)>([^<]+)',
        'my_gridsquare': r'<my_gridsquare:(\d+)>([^<]+)',
        'prop_mode': r'<prop_mode:(\d+)>([^<]+)',
        'sat_name': r'<sat_name:(\d+)>([^<]+)',
        'sat_mode': r'<sat_mode:(\d+)>([^<]+)',
        'station_callsign': r'<station_callsign:(\d+)>([^<]+)',
        'country': r'<country:(\d+)>([^<]+)',
        'cont': r'<cont:(\d+)>([^<]+)',
        'cqz': r'<cqz:(\d+)>(\d+)',
        'ituz': r'<ituz:(\d+)>(\d+)',
        'dxcc': r'<dxcc:(\d+)>(\d+)',
        'operator': r'<operator:(\d+)>([^<]+)'
    }

    date_value = None
    time_value = None

    for field, pattern in patterns.items():
        match = re.search(pattern, record, re.IGNORECASE)
        if match:
            if field == 'qso_date':
                value = match.group(2)
                if len(value) == 8:
                    year = int(value[:4])
                    month = int(value[4:6])
                    day = int(value[6:8])
                    date_value = date(year, month, day)

            elif field == 'time_on':
                time_str = match.group(2)
                if len(time_str) == 4:
                    hour = int(time_str[:2])
                    minute = int(time_str[2:4])
                    time_value = time(hour, minute)
                elif len(time_str) == 6:
                    hour = int(time_str[:2])
                    minute = int(time_str[2:4])
                    second = int(time_str[4:6])
                    time_value = time(hour, minute, second)

            elif field == 'freq':
                try:
                    freq_str = match.group(2).strip()
                    if freq_str and all(c in '0123456789.+-eE' for c in freq_str):
                        freq_value = float(freq_str)
                        if 0.1 <= freq_value <= 300000.0:
                            data['frequency'] = freq_value
                        else:
                            data['frequency'] = 0.0
                    else:
                        data['frequency'] = 0.0
                except (ValueError, OverflowError):
                    data['frequency'] = 0.0

            elif field == 'mode':
                mode_value = match.group(2).strip().upper()
                mode_mapping = {
                    'SSB': 'SSB', 'CW': 'CW', 'FM': 'FM', 'AM': 'AM', 'RTTY': 'RTTY',
                    'PSK31': 'PSK31', 'PSK63': 'PSK63', 'FT8': 'FT8', 'FT4': 'FT4',
                    'JT65': 'JT65', 'JT9': 'JT9', 'SSTV': 'SSTV', 'JS8': 'JS8',
                    'MSK144': 'MSK144', 'MFSK': 'MFSK'
                }
                data['mode'] = mode_mapping.get(mode_value, 'SSB')

            else:
                data[field] = match.group(2).strip()

    # Устанавливаем дату и время
    if date_value:
        data['date'] = date_value
    else:
        data['date'] = date.today()

    if time_value:
        data['time'] = time_value
    else:
        data['time'] = time(0, 0)

    # Если нет позывного, пропускаем запись
    if 'callsign' not in data or not data['callsign']:
        return None

    # Значения по умолчанию
    if 'mode' not in data:
        data['mode'] = 'SSB'
    if 'frequency' not in data:
        data['frequency'] = 0.0

    # Обработка локаторов
    if 'gridsquare' in data:
        data['his_gridsquare'] = data['gridsquare']
    if 'my_gridsquare' in data:
        data['my_gridsquare'] = data['my_gridsquare']

    return data


def delete_adif_uploads(request, upload_id):
    """
    Удаляет записи QSO, связанные с загруженным ADIF файлом,
    и удаляет запись о загрузке файла
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Получаем запись о загрузке
        try:
            adif_upload = ADIFUpload.objects.get(id=upload_id, user=request.user)
        except ADIFUpload.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Загрузка файла не найдена'
            }, status=404)

        # Подсчитываем количество связанных QSO
        qso_count = QSO.objects.filter(adif_upload=adif_upload).count()

        # Удаляем связанные записи QSO
        deleted_qso_count, _ = QSO.objects.filter(adif_upload=adif_upload).delete()

        # Удаляем запись о загрузке
        adif_upload.delete()

        return JsonResponse({
            'success': True,
            'message': f'Удалено {deleted_qso_count} записей QSO из файла "{adif_upload.file_name}"',
            'stats': {
                'deleted_qso': deleted_qso_count,
                'file_name': adif_upload.file_name
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при удалении: {str(e)}'
        }, status=500)