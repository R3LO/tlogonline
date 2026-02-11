# Конвертер ADIF файлов QO-100

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from ..models import check_user_blocked
import os
import uuid
import re


@login_required
@xframe_options_exempt
def qo100_converter(request):
    """
    Конвертер ADIF файлов для QO-100
    """
    print(f"[QO-100 DEBUG] qo100_converter called, method={request.method}")

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    preview = None
    download_url = None
    download_filename = None

    # Определяем шаблон для отображения (iframe или полный)
    is_iframe = request.GET.get('iframe') == '1'
    template_name = 'qo100/converter_iframe.html' if is_iframe else 'qo100/converter.html'

    if request.method == 'POST':
        try:
            adif_file = request.FILES.get('adif_file')
            print(f"[QO-100 DEBUG] adif_file={adif_file}")

            if not adif_file:
                messages.error(request, 'Пожалуйста, выберите файл для загрузки')
                return render(request, template_name, {
                    'preview': preview,
                    'download_url': download_url,
                    'download_filename': download_filename,
                })

            # Читаем содержимое файла
            content = adif_file.read().decode('utf-8', errors='ignore')
            print(f"[QO-100 DEBUG] content length={len(content)}")

            # Переводим в верхний регистр для统一 обработки
            content = content.upper()

            # Проверяем наличие обязательного тега EOH
            if 'EOH' not in content:
                messages.error(request, 'Некорректный ADIF файл: отсутствует тег EOH')
                return render(request, template_name, {
                    'preview': preview,
                    'download_url': download_url,
                    'download_filename': download_filename,
                })

            # Обрабатываем файл
            result = process_adif_content(content)
            print(f"[QO-100 DEBUG] process_adif_content result={result}")
            
            if 'error' in result:
                messages.error(request, result['error'])
                return render(request, template_name, {
                    'preview': preview,
                    'download_url': download_url,
                    'download_filename': download_filename,
                })

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

            messages.success(request, f'Файл успешно обработан. Обработано QSO: {result["qso_count"]}')

        except Exception as e:
            import traceback
            print(f"[QO-100 DEBUG] Exception: {str(e)}")
            print(f"[QO-100 DEBUG] Traceback: {traceback.format_exc()}")
            messages.error(request, f'Ошибка при обработке файла: {str(e)}')

    return render(request, template_name, {
        'preview': preview,
        'download_url': download_url,
        'download_filename': download_filename,
    })


def process_adif_content(content):
    """
    Обработка содержимого ADIF файла - конвертирует все QSO в формат QO-100
    """
    try:
        print(f"[QO-100 DEBUG] Starting process_adif_content, content length: {len(content)}")

        # Разделяем на заголовок и данные
        eoh_pos = content.find('EOH')
        if eoh_pos == -1:
            print("[QO-100 DEBUG] EOH tag not found")
            return {'error': 'Некорректный ADIF файл: отсутствует тег EOH'}
        
        print(f"[QO-100 DEBUG] EOH found at position {eoh_pos}")

        header = content[:eoh_pos + 3]
        data = content[eoh_pos + 3:]
        
        print(f"[QO-100 DEBUG] Header length: {len(header)}, Data length: {len(data)}")

        # Парсим записи QSO из данных
        qso_records = parse_adif_records_simple(data)
        print(f"[QO-100 DEBUG] Parsed {len(qso_records)} QSO records")
        
        if not qso_records:
            print("[QO-100 DEBUG] No QSO records found")
            return {'error': 'В файле не найдено записей QSO'}
        
        # Обрабатываем все QSO - конвертируем в формат QO-100
        processed_qso = []
        download_content = []
        
        for i, record in enumerate(qso_records):
            print(f"[QO-100 DEBUG] Processing record {i}: {record}")
            processed_record = convert_qso_to_qo100(record)
            print(f"[QO-100 DEBUG] Converted record {i}: {processed_record}")

            if processed_record:
                processed_qso.append(processed_record)
                # Добавляем в содержимое для скачивания
                download_content.append(format_qso_for_download(processed_record))

        if not processed_qso:
            print("[QO-100 DEBUG] No successfully processed QSOs")
            return {'error': 'Не удалось обработать записи QSO'}

        # Формируем превью (первые 10 записей)
        preview = processed_qso[:10]
        
        # Формируем содержимое для скачивания с заголовком
        header_lines = [
            '<ADIF_VER:5>3.1.0',
            '<PROGRAMID:8>TLOG CONVERTER',
            '<EOH>'
        ]
        header_text = '\n'.join(header_lines)

        # QSO записи разделены переносом строки
        download_text = header_text + '\n' + '\n'.join(download_content)

        print(f"[QO-100 DEBUG] Successfully processed {len(processed_qso)} QSOs")

        return {
            'preview': preview,
            'download_content': download_text,
            'qso_count': len(processed_qso)
        }
        
    except Exception as e:
        import traceback
        print(f"[QO-100 DEBUG] Exception in process_adif_content: {str(e)}")
        print(f"[QO-100 DEBUG] Traceback: {traceback.format_exc()}")
        return {'error': f'Ошибка при обработке файла: {str(e)}'}


def parse_adif_header(header):
    """
    Парсинг заголовка ADIF файла (больше не используется, оставлен для совместимости)
    """
    return {}


def parse_adif_records_simple(data):
    """
    Парсинг записей QSO из ADIF данных - упрощенная версия
    Обрабатывает формат: <FIELD:length>value (где value может содержать пробелы)
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
        # Формат: <FIELD:length>value
        # Значение начинается сразу после > и имеет указанную длину
        field_pattern = r'<([A-Z0-9_]+):(\d+)>([^<]+)'
        matches = re.findall(field_pattern, record_string)

        print(f"[QO-100 DEBUG] parse_adif_records_simple: Found {len(matches)} fields")

        for field_name, field_len, field_value in matches:
            field_name = field_name.upper()
            field_value = field_value.strip()

            # Обрезаем значение до указанной длины
            try:
                field_len_int = int(field_len)
                if len(field_value) > field_len_int:
                    field_value = field_value[:field_len_int]
            except ValueError:
                pass

            record[field_name] = field_value

        if record:
            print(f"[QO-100 DEBUG] parse_adif_records_simple: Parsed record: {record}")
            records.append(record)

    return records


def convert_qso_to_qo100(record):
    """
    Конвертирует QSO в формат QO-100
    - Оставляет все поля как есть
    - Исправляет BAND на 13CM
    - Устанавливает PROP_MODE=SAT
    - Устанавливает SAT_NAME=QO-100
    """
    try:
        print(f"[QO-100 DEBUG] convert_qso_to_qo100: Input record: {record}")

        # Копируем все поля из исходной записи
        converted = record.copy()

        # Исправляем BAND на 13CM
        if 'BAND' in converted:
            converted['BAND'] = '13CM'

        # Устанавливаем PROP_MODE=SAT
        converted['PROP_MODE'] = 'SAT'

        # Устанавливаем SAT_NAME=QO-100
        converted['SAT_NAME'] = 'QO-100'

        print(f"[QO-100 DEBUG] convert_qso_to_qo100: Converted record: {converted}")

        return converted

    except Exception as e:
        print(f"[QO-100 DEBUG] convert_qso_to_qo100: Exception: {str(e)}")
        return None


def format_qso_for_download(record):
    """
    Форматирование записи QSO для скачивания
    Все теги в одной строке, разделённые пробелами, перенос только после <EOR>
    """
    tags = []

    # Форматируем поля для ADIF
    for field, value in record.items():
        if value:
            # Приводим к верхнему регистру
            field = field.upper()
            value = str(value).upper()

            if field == 'QSO_DATE':
                # Дата в формате YYYYMMDD
                date_value = value.replace('-', '')
                tags.append(f"<{field}:{len(date_value)}>{date_value}")
            elif field == 'TIME_ON':
                # Время в формате HHMMSS или HHMM
                time_value = value.replace(':', '').replace('-', '')
                tags.append(f"<{field}:{len(time_value)}>{time_value}")
            else:
                tags.append(f"<{field}:{len(value)}>{value}")

    tags.append("<EOR>")
    # Все теги в одной строке, разделённые пробелами
    return ' '.join(tags)


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