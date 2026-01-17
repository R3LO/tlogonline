"""
Представления для фронтенда (веб-страницы)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
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
    if request.method == 'POST':
        import json
        from django.contrib.auth.models import User
        from .models import RadioProfile

        # Действующий позывной используется как логин
        callsign = request.POST.get('callsign', '').strip().upper()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        qth = request.POST.get('qth', '').strip()
        qth_locator = request.POST.get('qth_locator', '').strip().upper()

        # Получаем список дополнительных позывных
        my_callsigns_list = request.POST.getlist('my_callsigns')
        # Фильтруем и очищаем
        my_callsigns = [c.strip().upper() for c in my_callsigns_list if c.strip()]

        # Валидация
        if not all([callsign, email, password, password_confirm]):
            messages.error(request, 'Все обязательные поля должны быть заполнены')
            return render(request, 'register_new.html')

        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register_new.html')

        if len(password) < 8:
            messages.error(request, 'Пароль должен содержать минимум 8 символов')
            return render(request, 'register_new.html')

        # Проверяем уникальность позывного (как username)
        if User.objects.filter(username=callsign).exists():
            messages.error(request, 'Пользователь с таким позывным уже существует')
            return render(request, 'register_new.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'register_new.html')

        # Создаем пользователя (позывной = username)
        try:
            user = User.objects.create_user(
                username=callsign,
                email=email,
                password=password
            )

            # Создаем профиль радиолюбителя
            RadioProfile.objects.create(
                user=user,
                callsign=callsign,
                first_name=first_name,
                last_name=last_name,
                qth=qth,
                my_gridsquare=qth_locator,
                my_callsigns=my_callsigns  # JSON список
            )

            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login_page')

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'register_new.html')

    return render(request, 'register_new.html')


def login_page(request):
    """
    Страница входа
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberMe')

        # Проверяем обязательные поля
        if not username or not password:
            messages.error(request, 'Имя пользователя и пароль обязательны')
            return render(request, 'login.html')

        # Аутентификация
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Если отмечен "Запомнить меня", сохраняем данные в cookies
            if remember_me:
                response = redirect('dashboard')
                response.set_cookie('remembered_username', username, 30*24*60*60)
                response.set_cookie('remembered_password', password, 30*24*60*60)
                return response
            else:
                response = redirect('dashboard')
                response.delete_cookie('remembered_username')
                response.delete_cookie('remembered_password')
                return response
        else:
            messages.error(request, 'Неверные учетные данные')
            return render(request, 'login.html')

    return render(request, 'login.html')


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

    # Обработка формы ручного ввода QSO
    if request.method == 'POST' and request.POST.get('action') == 'add_qso':
        try:
            from .models import QSO, RadioProfile, ADIFUpload
            from datetime import date, time
            from django.db.utils import IntegrityError

            # Получаем данные из формы
            my_callsign = request.POST.get('my_callsign', '').strip()
            callsign = request.POST.get('callsign', '').strip()
            date_str = request.POST.get('date', '').strip()
            time_str = request.POST.get('time', '').strip()
            band = request.POST.get('band', '').strip()
            mode = request.POST.get('mode', '').strip()
            rst_rcvd = request.POST.get('rst_rcvd', '').strip()
            rst_sent = request.POST.get('rst_sent', '').strip()
            his_gridsquare = request.POST.get('his_gridsquare', '').strip()
            his_qth = request.POST.get('his_qth', '').strip()

            # Валидация обязательных полей
            if not all([my_callsign, callsign, date_str, time_str, band, mode]):
                messages.error(request, 'Все обязательные поля должны быть заполнены')
                return redirect('dashboard')

            # Валидация форматов
            if len(my_callsign) > 20 or len(callsign) > 20:
                messages.error(request, 'Позывной не должен превышать 20 символов')
                return redirect('dashboard')

            if len(his_gridsquare) > 8:
                messages.error(request, 'QTH локатор не должен превышать 8 символов')
                return redirect('dashboard')

            # Парсинг даты и времени
            try:
                qso_date = date.fromisoformat(date_str)
                qso_time = time.fromisoformat(time_str)
            except ValueError:
                messages.error(request, 'Неверный формат даты или времени')
                return redirect('dashboard')

            # Проверка на дубликат
            duplicate_exists = QSO.objects.filter(
                user=request.user,
                my_callsign=my_callsign,
                callsign=callsign,
                date=qso_date,
                time=qso_time,
                band=band,
                mode=mode
            ).exists()

            if duplicate_exists:
                messages.warning(request, 'QSO с такими данными уже существует в логе')
                return redirect('dashboard')

            # Определение частоты по диапазону (упрощенное сопоставление)
            band_frequencies = {
                '160m': 1.9,
                '80m': 3.7,
                '40m': 7.1,
                '30m': 10.15,
                '20m': 14.2,
                '17m': 18.12,
                '15m': 21.3,
                '12m': 24.95,
                '10m': 28.5,
                '6m': 52.0,
                '2m': 144.0,
                '70cm': 435.0,
                '23cm': 1290.0,
                '13cm': 2400.0,
                '3cm': 10000.0
            }

            frequency = band_frequencies.get(band, 0.0)

            # Создание записи QSO
            try:
                qso_record = QSO.objects.create(
                    user=request.user,
                    my_callsign=my_callsign,
                    callsign=callsign,
                    date=qso_date,
                    time=qso_time,
                    frequency=frequency,
                    band=band,
                    mode=mode,
                    rst_rcvd=rst_rcvd if rst_rcvd else None,
                    rst_sent=rst_sent if rst_sent else None,
                    his_gridsquare=his_gridsquare if his_gridsquare else None,
                    his_qth=his_qth if his_qth else None,
                    lotw_qsl='N',
                    paper_qsl='N'
                )

                messages.success(request, f'QSO с {callsign} успешно добавлено в лог')
                return redirect('dashboard')

            except IntegrityError as e:
                messages.error(request, f'Ошибка при сохранении QSO: {str(e)}')
                return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Ошибка при обработке формы: {str(e)}')
            return redirect('dashboard')

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
    unique_callsigns = user_qso.values('callsign').distinct().count()

    # Статистика по видам модуляции
    mode_stats = {}
    mode_choices = dict(QSO._meta.get_field('mode').choices)
    for mode in mode_choices.keys():
        count = user_qso.filter(mode=mode).count()
        if count > 0:
            mode_stats[mode] = count

    # Последние QSO (последние 20)
    recent_qso = user_qso.order_by('-date', '-time')[:20]

    # Получаем загруженные ADIF файлы
    adif_uploads = ADIFUpload.objects.filter(user=request.user).order_by('-upload_date')[:5]

    context = {
        'user': request.user,
        'profile': profile,
        'total_qso': total_qso,
        'unique_callsigns': unique_callsigns,
        'recent_qso': recent_qso,
        'mode_statistics': mode_stats,
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
                            rst_rcvd = qso_data.get('rst_rcvd', '').strip()[:10]
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
                                rst_rcvd=rst_rcvd,
                                my_gridsquare=my_gridsquare,
                                his_gridsquare=his_gridsquare,
                                lotw_qsl='N',
                                paper_qsl='N'
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

    # Обработка RST - используем rst_rcvd (новое имя поля)
    # rst_rcvd уже извлекается паттерном выше

    return data


def logout_view(request):
    """
    Выход пользователя
    """
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')


def profile_update(request):
    """
    Обновление профиля радиолюбителя
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    if request.method == 'POST':
        try:
            from .models import RadioProfile

            # Получаем или создаем профиль
            profile, created = RadioProfile.objects.get_or_create(
                user=request.user,
                defaults={}
            )

            # Обновляем поля профиля
            profile.callsign = request.POST.get('callsign', '').strip()
            profile.full_name = request.POST.get('full_name', '').strip()
            profile.qth = request.POST.get('qth', '').strip()
            profile.my_gridsquare = request.POST.get('my_gridsquare', '').strip().upper()

            profile.save()

            messages.success(request, 'Профиль успешно обновлён')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')

    return redirect('dashboard')


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


def logbook_search(request, callsign):
    """
    Поиск по логам пользователя по позывному.
    Доступен по адресу /<callsign>/
    """
    from .models import QSO, RadioProfile

    # Нормализуем позывной (верхний регистр, без пробелов)
    callsign = callsign.strip().upper()

    # Проверяем, есть ли записи с таким my_callsign
    has_logs = QSO.objects.filter(my_callsign=callsign).exists()

    if not has_logs:
        # Если записей с таким позывным нет, показываем сообщение
        context = {
            'callsign': callsign,
            'has_logs': False,
            'error_message': f'Лог с позывным "{callsign}" не найден в базе данных.',
        }
        return render(request, 'logbook_search.html', context)

    # Получаем параметр поиска из формы
    search_callsign = request.GET.get('callsign', '').strip()

    context = {
        'callsign': callsign,
        'has_logs': True,
        'search_callsign': search_callsign,
        'qso_list': None,
    }

    # Если введен позывной для поиска - выполняем поиск
    if search_callsign:
        # Получаем QSO для этого позывного с фильтром по callsign корреспондента
        qso_queryset = QSO.objects.filter(
            my_callsign=callsign,
            callsign__icontains=search_callsign
        ).order_by('-date', '-time')

        # Подсчитываем статистику
        total_qso = qso_queryset.count()
        unique_callsigns = qso_queryset.values('callsign').distinct().count()

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

        # Пагинация
        page_size = 50
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        qso_list = qso_queryset[start:end]
        total_pages = (total_qso + page_size - 1) // page_size

        # Получаем уникальные режимы для фильтрации
        unique_modes = qso_queryset.values_list('mode', flat=True).distinct().order_by('mode')

        context.update({
            'qso_list': qso_list,
            'current_page': page,
            'total_pages': total_pages,
            'page_size': page_size,
            'band_stats': band_stats,
            'get_band_from_frequency': get_band_from_frequency,
        })

    return render(request, 'logbook_search.html', context)