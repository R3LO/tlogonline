"""
Представления для фронтенда (веб-страницы)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import uuid
from datetime import datetime
from .models import QSO


def home(request):
    """
    Главная страница
    """
    return render(request, 'index.html')


def register_page(request):
    """
    Страница регистрации
    """
    return render(request, 'register.html')


def login_page(request):
    """
    Страница входа
    """
    return render(request, 'login.html')


@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    """
    API для регистрации через веб-интерфейс
    """
    try:
        data = json.loads(request.body)

        # Проверяем обязательные поля
        required_fields = ['username', 'email', 'password', 'password_confirm']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'Поле {field} обязательно для заполнения'
                }, status=400)

        # Проверяем совпадение паролей
        if data['password'] != data['password_confirm']:
            return JsonResponse({
                'success': False,
                'error': 'Пароли не совпадают'
            }, status=400)

        # Проверяем уникальность username
        from django.contrib.auth.models import User
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({
                'success': False,
                'error': 'Пользователь с таким именем уже существует'
            }, status=400)

        # Проверяем уникальность email
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({
                'success': False,
                'error': 'Пользователь с таким email уже существует'
            }, status=400)

        # Создаем пользователя
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )

        return JsonResponse({
            'success': True,
            'message': 'Регистрация успешна! Теперь вы можете войти в систему.',
            'redirect_url': '/login/'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка сервера: {str(e)}'
        }, status=500)


def login_api(request):
    """
    API для входа через веб-интерфейс
    """
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember_me = request.POST.get('rememberMe')

            # Проверяем обязательные поля
            if not username or not password:
                messages.error(request, 'Имя пользователя и пароль обязательны')
                return redirect('login_page')

            # Аутентификация
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Если отмечен "Запомнить меня", сохраняем данные в cookies
                if remember_me:
                    # Сохраняем в cookies на 30 дней
                    response = redirect('dashboard')
                    response.set_cookie('remembered_username', username, 30*24*60*60)
                    response.set_cookie('remembered_password', password, 30*24*60*60)
                    return response
                else:
                    # Удаляем cookies если не отмечен "Запомнить меня"
                    response = redirect('dashboard')
                    response.delete_cookie('remembered_username')
                    response.delete_cookie('remembered_password')
                    return response
            else:
                messages.error(request, 'Неверные учетные данные')
                return redirect('login_page')

        except Exception as e:
            messages.error(request, f'Ошибка сервера: {str(e)}')
            return redirect('login_page')

    # Если GET запрос, перенаправляем на страницу логина
    return redirect('login_page')


def get_band_from_frequency(frequency):
    """
    Определяет диапазон по частоте
    """
    if frequency is None:
        return 'Unknown'

    band_ranges = {
        '160m': (1.8, 2.0),
        '80m': (3.5, 4.0),
        '40m': (7.0, 7.3),
        '30m': (10.1, 10.15),
        '20m': (14.0, 14.35),
        '17m': (18.068, 18.168),
        '15m': (21.0, 21.45),
        '12m': (24.89, 24.99),
        '10m': (28.0, 29.7),
        '6m': (50.0, 54.0),
        '4m': (70.0, 70.5),
        '2m': (144.0, 148.0),
        '70cm': (420.0, 450.0),
        '23cm': (1240.0, 1300.0),
        '13cm': (2400.0, 2500.0),
    }

    for band, (min_freq, max_freq) in band_ranges.items():
        if min_freq <= frequency <= max_freq:
            return band

    return f"{frequency:.1f}MHz"


def logbook(request):
    """
    Журнал QSO с поиском и фильтрацией
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    from .models import QSO, RadioProfile

    # Получаем параметры поиска и фильтрации
    search_query = request.GET.get('search', '').strip()
    callsign_filter = request.GET.get('callsign', '').strip()
    qth_filter = request.GET.get('qth', '').strip()
    mode_filter = request.GET.get('mode', '').strip()
    band_filter = request.GET.get('band', '').strip()

    # Базовый QuerySet для QSO пользователя
    qso_queryset = QSO.objects.filter(user=request.user)

    # Применяем поиск
    if search_query:
        qso_queryset = qso_queryset.filter(
            Q(callsign__icontains=search_query) |
            Q(his_gridsquare__icontains=search_query)
        )

    # Применяем фильтры
    if callsign_filter:
        qso_queryset = qso_queryset.filter(callsign__icontains=callsign_filter)

    if qth_filter:
        qso_queryset = qso_queryset.filter(his_gridsquare__icontains=qth_filter)

    if mode_filter:
        qso_queryset = qso_queryset.filter(mode=mode_filter)

    if band_filter:
        # Фильтрация по диапазону на основе частоты
        band_ranges = {
            '160m': (1.8, 2.0),
            '80m': (3.5, 4.0),
            '40m': (7.0, 7.3),
            '30m': (10.1, 10.15),
            '20m': (14.0, 14.35),
            '17m': (18.068, 18.168),
            '15m': (21.0, 21.45),
            '12m': (24.89, 24.99),
            '10m': (28.0, 29.7),
            '6m': (50.0, 54.0),
            '4m': (70.0, 70.5),
            '2m': (144.0, 148.0),
            '70cm': (420.0, 450.0),
            '23cm': (1240.0, 1300.0),
            '13cm': (2400.0, 2500.0),
        }

        if band_filter in band_ranges:
            min_freq, max_freq = band_ranges[band_filter]
            qso_queryset = qso_queryset.filter(
                frequency__gte=min_freq,
                frequency__lte=max_freq
            )

    # Сортируем по дате (новые сверху)
    qso_queryset = qso_queryset.order_by('-date', '-time')

    # Пагинация (50 записей на страницу)
    page_size = 50
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size

    qso_list = qso_queryset[start:end]
    total_count = qso_queryset.count()
    total_pages = (total_count + page_size - 1) // page_size

    # Получаем уникальные значения для фильтров
    unique_modes = qso_queryset.values_list('mode', flat=True).distinct().order_by('mode')

    # Подсчитываем статистику для выбранных фильтров
    filtered_stats = {
        'total_qso': total_count,
        'unique_callsigns': qso_queryset.values('callsign').distinct().count(),
        'unique_qth': qso_queryset.filter(his_gridsquare__isnull=False).exclude(his_gridsquare='').values('his_gridsquare').distinct().count(),
        'unique_modes': len(unique_modes),
    }

    # Статистика по диапазонам
    band_stats = {}
    bands = ['160m', '80m', '40m', '20m', '15m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
    band_ranges = {
        '160m': (1.8, 2.0),
        '80m': (3.5, 4.0),
        '40m': (7.0, 7.3),
        '30m': (10.1, 10.15),
        '20m': (14.0, 14.35),
        '17m': (18.068, 18.168),
        '15m': (21.0, 21.45),
        '12m': (24.89, 24.99),
        '10m': (28.0, 29.7),
        '6m': (50.0, 54.0),
        '4m': (70.0, 70.5),
        '2m': (144.0, 148.0),
        '70cm': (420.0, 450.0),
        '23cm': (1240.0, 1300.0),
        '13cm': (2400.0, 2500.0),
    }

    for band in bands:
        if band in band_ranges:
            min_freq, max_freq = band_ranges[band]
            count = qso_queryset.filter(
                frequency__gte=min_freq,
                frequency__lte=max_freq
            ).count()
            if count > 0:
                band_stats[band] = count

    # Получаем позывной пользователя из профиля
    try:
        user_callsign = request.user.radio_profile.callsign
    except RadioProfile.DoesNotExist:
        user_callsign = request.user.username

    context = {
        'user': request.user,
        'user_callsign': user_callsign,  # Мой позывной
        'qso_list': qso_list,
        'total_count': total_count,
        'current_page': page,
        'total_pages': total_pages,
        'page_size': page_size,

        # Параметры фильтрации для сохранения в форме
        'search_query': search_query,
        'callsign_filter': callsign_filter,
        'qth_filter': qth_filter,
        'mode_filter': mode_filter,
        'band_filter': band_filter,

        # Доступные варианты для фильтров
        'available_modes': unique_modes,
        'available_bands': list(band_stats.keys()),

        # Статистика
        'filtered_stats': filtered_stats,
        'band_stats': band_stats,

        # Helper функция для определения диапазона
        'get_band_from_frequency': get_band_from_frequency,
    }

    return render(request, 'logbook.html', context)


def dashboard(request):
    """
    Личный кабинет радиолюбителя
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Получаем профиль радиолюбителя
    from .models import QSO, RadioProfile, ADIFUpload

    try:
        profile = request.user.radio_profile
    except RadioProfile.DoesNotExist:
        profile = None

    # Получаем QSO пользователя
    user_qso = QSO.objects.filter(user=request.user)

    # Подсчитываем статистику
    total_qso = user_qso.count()

    # Статистика по видам модуляции
    mode_stats = {}
    mode_choices = dict(QSO._meta.get_field('mode').choices)
    for mode in mode_choices.keys():
        count = user_qso.filter(mode=mode).count()
        if count > 0:
            mode_stats[mode] = count

    # Статистика по диапазонам
    band_stats = {}
    bands = [
        ('160m', 1.8, 2.0),
        ('80m', 3.5, 4.0),
        ('40m', 7.0, 7.3),
        ('20m', 14.0, 14.35),
        ('15m', 21.0, 21.45),
        ('10m', 28.0, 29.7),
        ('6m', 50.0, 54.0),
        ('2m', 144.0, 148.0),
        ('70cm', 420.0, 450.0),
    ]

    for band_name, min_freq, max_freq in bands:
        count = user_qso.filter(frequency__gte=min_freq, frequency__lte=max_freq).count()
        if count > 0:
            band_stats[band_name] = count

    # Последние QSO (последние 20) - обновленный запрос для новых полей date/time
    recent_qso = user_qso.order_by('-date', '-time')[:20]

    # Получаем загруженные ADIF файлы
    adif_uploads = ADIFUpload.objects.filter(user=request.user).order_by('-upload_date')[:10]

    context = {
        'user': request.user,
        'profile': profile,
        'total_qso': total_qso,
        'recent_qso': recent_qso,
        'mode_statistics': mode_stats,
        'band_statistics': band_stats,
        'adif_uploads': adif_uploads,
    }

    return render(request, 'dashboard.html', context)


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
            from .models import ADIFUpload

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

            # Сохраняем файл (default_storage.save возвращает относительный путь)
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))

            # Запускаем обработку файла (передаем сохраненный путь)
            try:
                qso_count = process_adif_file(saved_path, request.user)

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


def process_adif_file(file_path, user):
    """
    Обрабатывает ADIF файл и создает записи QSO
    Оптимизированная версия с пакетной обработкой и проверкой дубликатов
    """
    from .models import QSO
    from django.db import transaction
    from django.core.exceptions import ValidationError

    # default_storage.save() возвращает путь относительно MEDIA_ROOT
    # Строим полный путь для чтения файла
    media_root = default_storage.location

    # Если файл уже сохранен через default_storage, file_path содержит относительный путь
    if not os.path.isabs(file_path):
        # Убираем дублирование 'media' в пути
        clean_path = file_path.replace('media/', '').replace('media\\', '')
        full_path = os.path.join(media_root, clean_path)
    else:
        full_path = file_path



    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Файл не найден: {full_path}")

    with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()

    # Парсер ADIF - извлекаем записи QSO
    qso_records = []

    # Разбиваем содержимое на строки
    lines = content.split('\n')
    in_qso_section = False
    current_record = []

    for line in lines:
        line = line.strip()

        # Пропускаем заголовки до <EOH> или <eoh>
        if line == '<EOH>' or line == '<eoh>':
            in_qso_section = True
            continue

        # Если в файле нет явного <EOH>, начинаем обработку после первой строки с позывным
        if not in_qso_section and '<call:' in line:
            in_qso_section = True

        # Обрабатываем записи QSO
        if in_qso_section and line:
            if line.startswith('<'):
                # Если это начало новой записи (начинается с поля)
                if current_record:
                    # Сохраняем предыдущую запись
                    full_record = ' '.join(current_record).replace('  ', ' ')
                    if full_record.strip():
                        qso_records.append(full_record.strip())
                    current_record = []

                current_record.append(line)
            else:
                # Продолжение текущей записи
                if current_record:
                    current_record.append(line)

    # Добавляем последнюю запись если есть
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

    # Пакетная обработка для оптимизации
    batch_size = 100  # Обрабатываем по 100 записей за раз
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
                    # Проверяем на дубликат перед созданием объекта
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
                        # Валидируем данные перед созданием объекта
                        try:
                            # Дополнительная валидация частоты
                            frequency = qso_data.get('frequency', 0.0)
                            if not isinstance(frequency, (int, float)) or frequency < 0:
                                frequency = 0.0

                            # Ограничиваем длину позывных
                            callsign = qso_data.get('callsign', '').strip()[:20]
                            my_callsign = user_callsign.strip()[:20]

                            # Ограничиваем длину строковых полей
                            band = qso_data.get('band', '').strip()[:10]
                            mode = qso_data.get('mode', 'SSB')
                            rst_sent = qso_data.get('rst_sent', '').strip()[:10]
                            rst_received = qso_data.get('rst_received', '').strip()[:10]
                            my_gridsquare = qso_data.get('my_gridsquare', '').strip()[:10]
                            his_gridsquare = qso_data.get('his_gridsquare', '').strip()[:10]

                            # Проверяем обязательные поля
                            if not callsign:
                                skipped_count += 1
                                continue

                            # Создаем объект QSO
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
                                rst_received=rst_received,
                                my_gridsquare=my_gridsquare,
                                his_gridsquare=his_gridsquare
                            )

                            # Проверяем валидность объекта (только критические поля)
                            if not qso_obj.callsign or not qso_obj.date or not qso_obj.time:
                                skipped_count += 1
                                continue
                            qso_objects.append(qso_obj)

                        except Exception:
                            error_count += 1
                            continue
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
            except Exception:
                error_count += 1
                continue

        # Пакетная вставка для повышения производительности
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
    import re
    from datetime import datetime, date, time

    data = {}

    # Извлекаем поля ADIF
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
        'rst_received': r'<rst_received:(\d+)>([^<]+)',
        'rst_rcvd': r'<rst_rcvd:(\d+)>([^<]+)',  # WSJT-X использует сокращенную форму
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
                    # Формат YYYYMMDD
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
                    # Проверяем, что строка содержит только допустимые символы для числа
                    if freq_str and all(c in '0123456789.+-eE' for c in freq_str):
                        freq_value = float(freq_str)
                        # Проверяем разумные пределы для радиочастот (0.1 МГц - 300 ГГц)
                        # В вашем файле частоты указаны в МГц (например, 2380.041260 МГц)
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
                # Нормализуем названия режимов
                mode_mapping = {
                    'SSB': 'SSB',
                    'CW': 'CW',
                    'FM': 'FM',
                    'AM': 'AM',
                    'RTTY': 'RTTY',
                    'PSK31': 'PSK31',
                    'PSK63': 'PSK63',
                    'FT8': 'FT8',
                    'FT4': 'FT4',
                    'JT65': 'JT65',
                    'JT9': 'JT9',
                    'SSTV': 'SSTV',
                    'JS8': 'JS8',
                    'MSK144': 'MSK144',
                    'MFSK': 'MFSK'  # Поддержка MFSK режимов
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

    # Устанавливаем значения по умолчанию
    if 'mode' not in data:
        data['mode'] = 'SSB'
    if 'frequency' not in data:
        data['frequency'] = 0.0

    # Обработка локаторов
    if 'gridsquare' in data:
        data['his_gridsquare'] = data['gridsquare']
    if 'my_gridsquare' in data:
        data['my_gridsquare'] = data['my_gridsquare']

    # Обработка RST - поддержка как rst_received, так и rst_rcvd (WSJT-X формат)
    if 'rst_rcvd' in data:
        data['rst_received'] = data['rst_rcvd']
        del data['rst_rcvd']  # Удаляем временное поле

    return data


def logout_view(request):
    """
    Выход пользователя
    """
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')


def clear_logbook(request):
    """
    Удаляет все записи QSO пользователя
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Подсчитываем количество записей для статистики
        qso_count = QSO.objects.filter(user=request.user).count()
        unique_callsigns = QSO.objects.filter(user=request.user).values('callsign').distinct().count()
        unique_qth = QSO.objects.filter(user=request.user).filter(his_gridsquare__isnull=False).exclude(his_gridsquare='').values('his_gridsquare').distinct().count()

        # Удаляем все записи пользователя
        deleted_count, _ = QSO.objects.filter(user=request.user).delete()

        return JsonResponse({
            'success': True,
            'message': f'Удалено {deleted_count} записей QSO',
            'stats': {
                'deleted_qso': deleted_count,
                'unique_callsigns': unique_callsigns,
                'unique_qth': unique_qth
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при удалении записей: {str(e)}'
        }, status=500)