"""
Представления для загрузки и обработки ADIF файлов
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from ..models import QSO, ADIFUpload
from .. import r150s
from ..region_ru import RussianRegionFinder
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
                return redirect('logbook')

            from ..models import ADIFUpload

            uploaded_file = request.FILES['file']

            # Проверяем расширение файла
            if not uploaded_file.name.lower().endswith(('.adi', '.adif')):
                messages.error(request, 'Неподдерживаемый формат файла. Разрешены только .adi и .adif файлы')
                return redirect('logbook')

            # Проверяем размер файла (максимум 20MB)
            if uploaded_file.size > 20 * 1024 * 1024:
                messages.error(request, 'Размер файла превышает 20MB')
                return redirect('logbook')

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

            # Получаем дополнительные параметры из формы
            add_extra_tags = request.POST.get('add_extra_tags') == 'on'
            my_callsign_default = request.POST.get('my_callsign', '').strip()[:20] if add_extra_tags and request.POST.get('override_my_callsign') == 'on' else None
            my_gridsquare_default = request.POST.get('my_gridsquare', '').strip()[:10] if add_extra_tags and request.POST.get('override_my_gridsquare') == 'on' else None
            prop_mode_default = request.POST.get('prop_mode', 'SAT').strip()[:50] if add_extra_tags and request.POST.get('override_prop_mode') == 'on' else None
            sat_name_default = request.POST.get('sat_name', 'QO-100').strip()[:50] if add_extra_tags and request.POST.get('override_sat_name') == 'on' else None

            # Запускаем обработку файла
            try:
                qso_count, updated_count = process_adif_file(
                    saved_path, request.user, adif_upload.id,
                    my_callsign_default=my_callsign_default,
                    my_gridsquare_default=my_gridsquare_default,
                    prop_mode_default=prop_mode_default,
                    sat_name_default=sat_name_default,
                    add_extra_tags=add_extra_tags
                )

                # Если добавлено 0 записей и нет обновлений, удаляем запись о загрузке и файл
                if qso_count == 0 and updated_count == 0:
                    adif_upload.delete()
                    # Удаляем файл
                    if default_storage.exists(saved_path):
                        default_storage.delete(saved_path)
                    messages.warning(request, f'Файл "{uploaded_file.name}" не содержит новых записей (все записи являются дубликатами).')
                else:
                    adif_upload.processed = True
                    adif_upload.qso_count = qso_count
                    adif_upload.save()
                    msg_parts = []
                    if qso_count > 0:
                        msg_parts.append(f'добавлено {qso_count} новых записей QSO')
                    if updated_count > 0:
                        msg_parts.append(f'обновлено {updated_count} записей с подтверждением LoTW')
                    messages.success(request, f'Файл "{uploaded_file.name}" успешно загружен и обработан. {", ".join(msg_parts)}.')

            except Exception as process_error:
                adif_upload.processed = True
                adif_upload.error_message = f'Ошибка обработки: {str(process_error)}'
                adif_upload.save()

                messages.warning(request, f'Файл "{uploaded_file.name}" загружен, но произошла ошибка при обработке: {str(process_error)}')

        except Exception as e:
            messages.error(request, f'Ошибка при загрузке файла: {str(e)}')

    return redirect('logbook')


def process_adif_file(file_path, user, adif_upload_id=None, my_callsign_default=None, my_gridsquare_default=None, prop_mode_default=None, sat_name_default=None, add_extra_tags=False):
    """
    Обрабатывает ADIF файл и создает записи QSO

    Args:
        file_path: Путь к файлу
        user: Пользователь
        adif_upload_id: ID записи ADIFUpload для связи с QSO
        my_callsign_default: Значение MY_CALLSIGN по умолчанию из формы
        my_gridsquare_default: Значение MY_GRIDSQUARE по умолчанию из формы
        prop_mode_default: Значение PROP_MODE по умолчанию из формы
        sat_name_default: Значение SAT_NAME по умолчанию из формы
    """
    # Получаем путь к базе r150s (файл находится в папке tlog)
    tlog_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(tlog_dir, 'r150cty.dat')

    # Инициализируем базы данных
    r150s.init_database(db_path)

    # Инициализируем определитель регионов России
    exceptions_path = os.path.join(tlog_dir, 'exceptions.dat')
    region_finder = RussianRegionFinder(exceptions_file=exceptions_path)

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

    # Получаем позывной пользователя из профиля (если не переопределен из формы)
    if not my_callsign_default:
        try:
            user_callsign = user.radio_profile.callsign
            if not user_callsign:
                user_callsign = user.username
        except:
            user_callsign = user.username
    else:
        user_callsign = my_callsign_default

    # Пакетная обработка - оптимизированная версия
    batch_size = 500  # Увеличиваем размер batch
    qso_count = 0
    skipped_count = 0
    error_count = 0
    updated_count = 0

    # Предварительная загрузка существующих QSO пользователя для проверки дубликатов
    # Словарь: ключ -> (id, lotw)
    existing_qsos = {}
    try:
        existing_db = QSO.objects.filter(user=user).values_list(
            'my_callsign', 'callsign', 'date', 'mode', 'band', 'id', 'lotw'
        )
        for item in existing_db:
            key = (
                str(item[0]).upper() if item[0] else '',
                str(item[1]).upper() if item[1] else '',
                item[2],
                str(item[3]).upper() if item[3] else '',
                str(item[4]).upper() if item[4] else ''
            )
            existing_qsos[key] = {'id': item[5], 'lotw': item[6]}
    except Exception:
        pass  # Если ошибка, продолжаем без кэша

    for i in range(0, len(qso_records), batch_size):
        batch = qso_records[i:i + batch_size]
        qso_objects = []
        qso_updates = {}  # {id: {'rst_sent': ..., 'rst_rcvd': ...}}

        for record in batch:
            try:
                qso_data = parse_adif_record(record)
                if qso_data:
                    callsign_qso = qso_data.get('callsign', '').strip().upper()[:20]
                    date_qso = qso_data.get('date')
                    time_qso = qso_data.get('time')
                    band_qso = qso_data.get('band', '').strip().upper()[:10]
                    mode_qso = qso_data.get('mode', 'SSB').upper()

                    # Быстрая проверка дубликатов через кэш
                    dup_key = (
                        user_callsign.upper() if user_callsign else '',
                        callsign_qso,
                        date_qso,
                        mode_qso,
                        band_qso
                    )

                    if dup_key in existing_qsos:
                        # Дубликат найден - проверяем lotw статус
                        existing = existing_qsos[dup_key]
                        if existing['lotw'] == 'Y':
                            # Обновляем только rst_sent и rst_rcvd для QSO с подтверждением LoTW
                            rst_sent = qso_data.get('rst_sent', '').strip().upper()[:10]
                            rst_rcvd = qso_data.get('rst_rcvd', '').strip().upper()[:10]
                            qso_updates[existing['id']] = {
                                'rst_sent': rst_sent if rst_sent else None,
                                'rst_rcvd': rst_rcvd if rst_rcvd else None
                            }
                            updated_count += 1
                        else:
                            skipped_count += 1
                    else:
                        # Валидация и очистка данных
                        frequency = qso_data.get('frequency', 0.0)
                        if not isinstance(frequency, (int, float)) or frequency < 0:
                            frequency = 0.0

                        callsign = callsign_qso
                        my_callsign = user_callsign.strip().upper()[:20] if user_callsign else None
                        band = band_qso
                        mode = mode_qso
                        rst_sent = qso_data.get('rst_sent', '').strip().upper()[:10]
                        rst_rcvd = qso_data.get('rst_rcvd', '').strip().upper()[:10]

                        # MY_CALLSIGN - приоритет: форма(если галочка) > OPERATOR > MY_CALLSIGN > профиль
                        my_callsign_adif = qso_data.get('my_callsign', '').strip().upper()[:20]
                        operator_adif = qso_data.get('operator', '').strip().upper()[:20]

                        # Если add_extra_tags И override_my_callsign, используем ТОЛЬКО из формы
                        if add_extra_tags and my_callsign_default:
                            my_callsign = my_callsign_default.upper()[:20]
                        # Иначе если есть OPERATOR в ADIF, используем его
                        elif operator_adif:
                            my_callsign = operator_adif
                        # Иначе если есть MY_CALLSIGN в ADIF, используем его
                        elif my_callsign_adif:
                            my_callsign = my_callsign_adif
                        # Иначе будет использоваться user_callsign из профиля
                        else:
                            my_callsign = None

                        # MY_GRIDSQUARE - если add_extra_tags И override_my_gridsquare, берём из формы
                        my_gridsquare_adif = qso_data.get('my_gridsquare', '').strip().upper()[:10]
                        if add_extra_tags and my_gridsquare_default:
                            my_gridsquare = my_gridsquare_default.upper()[:10]
                        else:
                            my_gridsquare = my_gridsquare_adif

                        gridsquare = qso_data.get('gridsquare', '').strip().upper()[:10]

                        # PROP_MODE - если add_extra_tags И override_prop_mode, берём из формы
                        prop_mode_adif = qso_data.get('prop_mode', '').strip().upper()[:50]
                        if add_extra_tags and prop_mode_default:
                            prop_mode = prop_mode_default.upper()[:50]
                        else:
                            prop_mode = prop_mode_adif

                        # SAT_NAME - если add_extra_tags И override_sat_name, берём из формы
                        sat_name_adif = qso_data.get('sat_name', '').strip().upper()[:50]
                        if add_extra_tags and sat_name_default:
                            sat_name = sat_name_default.upper()[:50]
                        else:
                            sat_name = sat_name_adif

                        cqz = qso_data.get('cqz')
                        ituz = qso_data.get('ituz')
                        continent = qso_data.get('cont', '').strip().upper()[:2]

                        # Если поля отсутствуют в ADIF, получаем из базы r150cty.dat
                        dxcc_info = r150s.get_dxcc_info(callsign, db_path)
                        if dxcc_info:
                            if not cqz:
                                cqz = dxcc_info.get('cq_zone')
                            if not ituz:
                                ituz = dxcc_info.get('itu_zone')
                            if not continent:
                                continent = dxcc_info.get('continent')

                        # Заполняем r150s данными country из r150cty.dat
                        r150s_country = None
                        if dxcc_info:
                            r150s_country = dxcc_info.get('country')
                            if r150s_country:
                                r150s_country = r150s_country.strip().upper()[:100]

                        if not callsign:
                            skipped_count += 1
                            continue

                        # Определяем код региона России только для российских позывных (UA-UG, R0-R9, RA-RZ)
                        state = None
                        callsign_upper = callsign.upper()
                        # Определяем российские позывные по префиксу без использования dxcc
                        # UA-UG - старые российские позывные, R0-R9, RA-RZ - новые российские позывные
                        if (callsign_upper.startswith('UA') or
                            callsign_upper.startswith('UB') or
                            callsign_upper.startswith('UC') or
                            callsign_upper.startswith('UD') or
                            callsign_upper.startswith('UE') or
                            callsign_upper.startswith('UF') or
                            callsign_upper.startswith('UG') or
                            callsign_upper.startswith('R0') or
                            callsign_upper.startswith('R1') or
                            callsign_upper.startswith('R2') or
                            callsign_upper.startswith('R3') or
                            callsign_upper.startswith('R4') or
                            callsign_upper.startswith('R5') or
                            callsign_upper.startswith('R6') or
                            callsign_upper.startswith('R7') or
                            callsign_upper.startswith('R8') or
                            callsign_upper.startswith('R9') or
                            callsign_upper.startswith('RA') or
                            callsign_upper.startswith('RB') or
                            callsign_upper.startswith('RC') or
                            callsign_upper.startswith('RD') or
                            callsign_upper.startswith('RE') or
                            callsign_upper.startswith('RF') or
                            callsign_upper.startswith('RG') or
                            callsign_upper.startswith('RH') or
                            callsign_upper.startswith('RI') or
                            callsign_upper.startswith('RJ') or
                            callsign_upper.startswith('RK') or
                            callsign_upper.startswith('RL') or
                            callsign_upper.startswith('RM') or
                            callsign_upper.startswith('RN') or
                            callsign_upper.startswith('RO') or
                            callsign_upper.startswith('RP') or
                            callsign_upper.startswith('RQ') or
                            callsign_upper.startswith('RR') or
                            callsign_upper.startswith('RS') or
                            callsign_upper.startswith('RT') or
                            callsign_upper.startswith('RU') or
                            callsign_upper.startswith('RV') or
                            callsign_upper.startswith('RW') or
                            callsign_upper.startswith('RX') or
                            callsign_upper.startswith('RY') or
                            callsign_upper.startswith('RZ')):
                            state = region_finder.get_region_code(callsign)

                        qso_obj = QSO(
                            user=user,
                            my_callsign=my_callsign if my_callsign else user_callsign,
                            callsign=callsign,
                            date=date_qso,
                            time=time_qso,
                            frequency=frequency,
                            band=band,
                            mode=mode,
                            rst_sent=rst_sent,
                            rst_rcvd=rst_rcvd,
                            my_gridsquare=my_gridsquare if my_gridsquare else None,
                            gridsquare=gridsquare if gridsquare else None,
                            prop_mode=prop_mode if prop_mode else None,
                            sat_name=sat_name if sat_name else None,
                            r150s=r150s_country if r150s_country else None,
                            cqz=cqz,
                            ituz=ituz,
                            continent=continent if continent else None,
                            lotw='N',
                            paper_qsl='N',
                            adif_upload_id=adif_upload_id,
                            state=state
                        )

                        if not qso_obj.callsign or not qso_obj.date or not qso_obj.time:
                            skipped_count += 1
                            continue
                        qso_objects.append(qso_obj)
            except Exception:
                error_count += 1
                continue

        # Пакетная вставка с ignore_conflicts
        if qso_objects:
            try:
                with transaction.atomic():
                    QSO.objects.bulk_create(qso_objects, batch_size=100, ignore_conflicts=True)
                    qso_count += len(qso_objects)
            except Exception:
                error_count += len(qso_objects)

        # Обновление QSO с подтверждением LoTW (только rst_sent и rst_rcvd)
        if qso_updates:
            try:
                with transaction.atomic():
                    # Получаем объекты QSO для обновления
                    qso_ids = list(qso_updates.keys())
                    qso_objects_to_update = list(QSO.objects.filter(id__in=qso_ids))

                    # Обновляем поля
                    for qso_obj in qso_objects_to_update:
                        if qso_obj.id in qso_updates:
                            update_data = qso_updates[qso_obj.id]
                            qso_obj.rst_sent = update_data['rst_sent']
                            qso_obj.rst_rcvd = update_data['rst_rcvd']

                    # Пакетное обновление по 1000 записей
                    if qso_objects_to_update:
                        QSO.objects.bulk_update(
                            qso_objects_to_update,
                            ['rst_sent', 'rst_rcvd'],
                            batch_size=1000
                        )
            except Exception:
                error_count += len(qso_updates)

    return qso_count, updated_count


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
        'submode': r'<submode:(\d+)>([^<]+)',
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
                data[field] = match.group(2).strip().upper()

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

    # Если MODE = MFSK, используем SUBMODE (если есть), иначе оставляем MFSK
    if data.get('mode', '').upper() == 'MFSK':
        if 'submode' in data and data['submode']:
            data['mode'] = data['submode'].strip().upper()

    if 'frequency' not in data:
        data['frequency'] = 0.0

    # Обработка локаторов
    if 'gridsquare' in data:
        data['gridsquare'] = data['gridsquare']
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