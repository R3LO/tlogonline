"""
Представления для работы с журналом QSO
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from datetime import datetime, time
from ..models import QSO, RadioProfile, ADIFUpload, check_user_blocked


def get_band_from_frequency(frequency):
    """
    Определяет диапазон по частоте
    """
    if frequency is None:
        return 'Unknown'

    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
        '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
        '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
        '4m': (70.0, 70.5), '2m': (144.0, 148.0), '70cm': (420.0, 450.0),
        '23cm': (1240.0, 1300.0), '13cm': (2400.0, 2500.0),
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

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    # Получаем параметры фильтрации
    search_callsign = request.GET.get('search_callsign', '').strip()
    search_qth = request.GET.get('search_qth', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    mode_filter = request.GET.get('mode', '').strip()
    band_filter = request.GET.get('band', '').strip()
    sat_name_filter = request.GET.get('sat_name', '').strip()
    lotw_filter = request.GET.get('lotw', '').strip()

    # Базовый QuerySet для QSO пользователя
    qso_queryset = QSO.objects.filter(user=request.user)

    # Применяем поиск по части позывного
    if search_callsign:
        qso_queryset = qso_queryset.filter(callsign__icontains=search_callsign)

    # Применяем поиск по части QTH локатора
    if search_qth:
        qso_queryset = qso_queryset.filter(gridsquare__icontains=search_qth)

    # Фильтр по дате "с"
    if date_from:
        qso_queryset = qso_queryset.filter(date__gte=date_from)

    # Фильтр по дате "до"
    if date_to:
        qso_queryset = qso_queryset.filter(date__lte=date_to)

    # Применяем фильтры
    if mode_filter:
        qso_queryset = qso_queryset.filter(mode=mode_filter)

    # Фильтр по диапазону - напрямую по полю band
    if band_filter:
        qso_queryset = qso_queryset.filter(band=band_filter)

    # Фильтр по SAT NAME
    if sat_name_filter:
        qso_queryset = qso_queryset.filter(sat_name=sat_name_filter)

    # Фильтр по LoTW
    if lotw_filter:
        qso_queryset = qso_queryset.filter(lotw=lotw_filter)

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

    # Уникальные значения для фильтров
    unique_modes = qso_queryset.values_list('mode', flat=True).distinct().order_by('mode')
    unique_bands = qso_queryset.values_list('band', flat=True).distinct().exclude(band__isnull=True).exclude(band='').order_by('band')
    unique_sat_names = qso_queryset.values_list('sat_name', flat=True).distinct().exclude(sat_name__isnull=True).exclude(sat_name='').order_by('sat_name')

    # Статистика для выбранных фильтров
    filtered_stats = {
        'total_qso': total_count,
        'unique_callsigns': qso_queryset.values('callsign').distinct().count(),
        'unique_dxcc': qso_queryset.filter(dxcc__isnull=False).exclude(dxcc='').values('dxcc').distinct().count(),
        'unique_r150s': qso_queryset.filter(r150s__isnull=False).exclude(r150s='').values('r150s').distinct().count(),
        'unique_ru_regions': qso_queryset.filter(ru_region__isnull=False).exclude(ru_region='').values('ru_region').distinct().count(),
    }

    # Статистика по диапазонам
    band_stats = {}
    bands = ['160m', '80m', '40m', '20m', '15m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
        '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
        '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
        '4m': (70.0, 70.5), '2m': (144.0, 148.0), '70cm': (420.0, 450.0),
        '23cm': (1240.0, 1300.0), '13cm': (2400.0, 2500.0),
    }

    for band in bands:
        if band in band_ranges:
            min_freq, max_freq = band_ranges[band]
            count = qso_queryset.filter(frequency__gte=min_freq, frequency__lte=max_freq).count()
            if count > 0:
                band_stats[band] = count

    # Позывной пользователя из профиля
    try:
        user_callsign = request.user.radio_profile.callsign
    except RadioProfile.DoesNotExist:
        user_callsign = request.user.username

    context = {
        'user': request.user,
        'user_callsign': user_callsign,
        'qso_list': qso_list,
        'total_count': total_count,
        'current_page': page,
        'total_pages': total_pages,
        'page_size': page_size,
        'search_callsign': search_callsign,
        'search_qth': search_qth,
        'date_from': date_from,
        'date_to': date_to,
        'mode_filter': mode_filter,
        'band_filter': band_filter,
        'sat_name_filter': sat_name_filter,
        'lotw_filter': lotw_filter,
        'available_modes': unique_modes,
        'available_bands': unique_bands,
        'available_sat_names': unique_sat_names,
        'filtered_stats': filtered_stats,
        'band_stats': band_stats,
        'get_band_from_frequency': get_band_from_frequency,
    }

    return render(request, 'logbook.html', context)


def logbook_search(request, callsign):
    """
    Поиск по логам пользователя по позывному.
    """
    # Проверяем, не заблокирован ли пользователь (если авторизован)
    if request.user.is_authenticated:
        is_blocked, reason = check_user_blocked(request.user)
        if is_blocked:
            return render(request, 'blocked.html', {'reason': reason})

    # Нормализуем позывной
    callsign = callsign.strip().upper()
    has_logs = QSO.objects.filter(my_callsign=callsign).exists()

    if not has_logs:
        return render(request, 'logbook_search.html', {
            'callsign': callsign,
            'has_logs': False,
            'error_message': f'Лог с позывным "{callsign}" не найден в базе данных.',
        })

    search_callsign = request.GET.get('callsign', '').strip()

    # Базовый queryset для всех QSO этого лога
    base_queryset = QSO.objects.filter(my_callsign=callsign)

    # Общее количество QSO в базе для этого позывного (без фильтров)
    total_qso_in_db = base_queryset.count()

    # Диапазоны и моды для матрицы
    bands = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
    modes = ['CW', 'SSB', 'FT8', 'FT4', 'RTTY', 'SSTV', 'MFSK', 'JT65', 'JT9', 'PSK31', 'AM', 'FM', 'DIG']

    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
        '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
        '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
        '2m': (144.0, 148.0), '70cm': (420.0, 450.0), '23cm': (1240.0, 1300.0),
        '13cm': (2300.0, 2450.0),  # Расширенный диапазон для 13cm
    }

    # Фильтруем по позывному корреспондента если задан
    if search_callsign:
        qso_queryset = base_queryset.filter(callsign__icontains=search_callsign).order_by('-date', '-time')
    else:
        qso_queryset = base_queryset.order_by('-date', '-time')

    total_qso = qso_queryset.count()

    # Формируем матрицу mode x band - используем поле band из базы
    # Формат: [[mode, band1_has, band2_has, ...], ...]
    matrix = []
    for mode in modes:
        row = [mode]
        for band in bands:
            count = qso_queryset.filter(
                Q(mode__iexact=mode) &
                (Q(band__iexact=band) | Q(frequency__gte=band_ranges[band][0], frequency__lte=band_ranges[band][1]))
            ).count()
            row.append(count > 0)
        matrix.append(row)

    # Пагинация для детальной таблицы
    page = int(request.GET.get('page', 1))
    page_size = 50
    start = (page - 1) * page_size
    end = start + page_size
    total_pages = (total_qso + page_size - 1) // page_size if total_qso > 0 else 1

    context = {
        'callsign': callsign,
        'has_logs': True,
        'search_callsign': search_callsign,
        'qso_list': qso_queryset[start:end],
        'total_qso': total_qso,
        'total_qso_in_db': total_qso_in_db,
        'matrix': matrix,
        'bands': bands,
        'modes': modes,
        'current_page': page,
        'total_pages': total_pages,
    }

    return render(request, 'logbook_search.html', context)


def clear_logbook(request):
    """
    Удаляет все записи QSO и загруженные ADIF файлы пользователя
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return JsonResponse({'error': 'Ваш аккаунт заблокирован'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Подсчитываем количество записей для статистики
        qso_count = QSO.objects.filter(user=request.user).count()
        unique_callsigns = QSO.objects.filter(user=request.user).values('callsign').distinct().count()
        unique_dxcc = QSO.objects.filter(user=request.user).filter(
            dxcc__isnull=False
        ).exclude(dxcc='').values('dxcc').distinct().count()
        unique_r150s = QSO.objects.filter(user=request.user).filter(
            r150s__isnull=False
        ).exclude(r150s='').values('r150s').distinct().count()
        adif_uploads_count = ADIFUpload.objects.filter(user=request.user).count()

        # Удаляем все записи QSO пользователя
        deleted_qso_count, _ = QSO.objects.filter(user=request.user).delete()

        # Удаляем все загруженные ADIF файлы пользователя
        deleted_adif_count, _ = ADIFUpload.objects.filter(user=request.user).delete()

        return JsonResponse({
            'success': True,
            'message': f'Удалено {deleted_qso_count} записей QSO и {deleted_adif_count} записей о загруженных файлах',
            'stats': {
                'deleted_qso': deleted_qso_count,
                'deleted_adif_uploads': deleted_adif_count,
                'unique_callsigns': unique_callsigns,
                'unique_dxcc': unique_dxcc,
                'unique_r150s': unique_r150s
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при удалении записей: {str(e)}'
        }, status=500)


@login_required
def edit_qso(request, qso_id):
    """
    Редактирование одной записи QSO
    """
    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return JsonResponse({'success': False, 'error': 'Ваш аккаунт заблокирован'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        qso = QSO.objects.get(id=qso_id, user=request.user)
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)

    try:
        import json
        from .. import r150s
        from ..region_ru import RussianRegionFinder
        import os
        from django.conf import settings

        data = json.loads(request.body)

        # Обновляем поля записи (все текстовые поля преобразуются в верхний регистр)
        qso.date = data.get('date')
        qso.time = data.get('time')
        qso.my_callsign = data.get('my_callsign', '').upper()[:20]
        qso.callsign = data.get('callsign', '').upper()[:20]
        qso.band = data.get('band', '').upper()[:10] or None
        qso.mode = (data.get('mode') or 'SSB').upper()

        frequency = data.get('frequency')
        if frequency:
            try:
                qso.frequency = float(frequency)
            except (ValueError, TypeError):
                qso.frequency = None
        else:
            qso.frequency = None

        qso.rst_rcvd = data.get('rst_rcvd', '').upper()[:10] or None
        qso.rst_sent = data.get('rst_sent', '').upper()[:10] or None
        qso.my_gridsquare = data.get('my_gridsquare', '').upper()[:10] or None
        qso.gridsquare = data.get('gridsquare', '').upper()[:10] or None
        qso.sat_name = data.get('sat_name', '').upper()[:50] or None
        qso.prop_mode = data.get('prop_mode', '').upper()[:50] or None

        qso.paper_qsl = data.get('paper_qsl', 'N')

        # Пересчитываем cqz, ituz, continent, r150s, dxcc, ru_region по позывному
        callsign = qso.callsign
        if callsign:
            # Инициализируем базы данных CTY и R150
            tlog_dir = os.path.join(settings.BASE_DIR, 'tlog')
            db_path = os.path.join(tlog_dir, 'r150cty.dat')
            cty_path = os.path.join(tlog_dir, 'cty.dat')

            r150s.init_database(db_path)
            r150s.init_cty_database(cty_path)

            dxcc_info = r150s.get_dxcc_info(callsign, db_path)
            if dxcc_info:
                qso.cqz = dxcc_info.get('cq_zone')
                qso.ituz = dxcc_info.get('itu_zone')
                qso.continent = dxcc_info.get('continent')

                r150s_country = dxcc_info.get('country')
                if r150s_country:
                    qso.r150s = r150s_country.upper()[:100]
                else:
                    qso.r150s = None

                dxcc = r150s.get_cty_primary_prefix(callsign, cty_path)
                if dxcc:
                    qso.dxcc = dxcc.upper()[:10]
                else:
                    qso.dxcc = None
            else:
                qso.cqz = None
                qso.ituz = None
                qso.continent = None
                qso.r150s = None
                qso.dxcc = None

            # Определяем код региона России только для российских позывных (UA, UA9, UA2)
            if qso.dxcc and qso.dxcc.upper() in ('UA', 'UA9', 'UA2'):
                exceptions_path = os.path.join(settings.BASE_DIR, 'tlog', 'exceptions.dat')
                region_finder = RussianRegionFinder(exceptions_file=exceptions_path)
                qso.ru_region = region_finder.get_region_code(callsign)
            else:
                qso.ru_region = None

        qso.save()

        return JsonResponse({'success': True, 'message': 'Запись успешно обновлена'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def delete_qso(request, qso_id):
    """
    Удаление одной записи QSO
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        qso = QSO.objects.get(id=qso_id, user=request.user)
        qso.delete()
        return JsonResponse({'success': True, 'message': 'Запись успешно удалена'})
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_qso(request, qso_id):
    """
    Получение данных одной записи QSO в формате JSON
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    try:
        qso = QSO.objects.get(id=qso_id, user=request.user)
        return JsonResponse({
            'success': True,
            'qso': {
                'id': str(qso.id),
                'date': qso.date.isoformat() if qso.date else None,
                'time': qso.time.isoformat() if qso.time else None,
                'my_callsign': qso.my_callsign or '',
                'callsign': qso.callsign or '',
                'band': qso.band or '',
                'mode': qso.mode or 'SSB',
                'frequency': qso.frequency,
                'rst_rcvd': qso.rst_rcvd or '',
                'rst_sent': qso.rst_sent or '',
                'my_gridsquare': qso.my_gridsquare or '',
                'gridsquare': qso.gridsquare or '',
                'sat_name': qso.sat_name or '',
                'prop_mode': qso.prop_mode or '',
                'cqz': qso.cqz,
                'ituz': qso.ituz,
                'lotw': qso.lotw or 'N',
                'continent': qso.continent or '',
                'r150s': qso.r150s or '',
                'dxcc': qso.dxcc or '',
                'ru_region': qso.ru_region or '',
                'paper_qsl': qso.paper_qsl or 'N',
            }
        })
    except (QSO.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def privacy(request):
    """
    Страница политики конфиденциальности
    """
    return render(request, 'privacy.html')


def qth_map(request):
    """
    Карта QTH локаторов пользователя
    """
    from ..models import QSO

    # Получаем все уникальные QTH локаторы из связей пользователя
    qso_list = QSO.objects.filter(user=request.user, gridsquare__isnull=False).exclude(gridsquare='')

    # Группируем по локаторам с подсчетом количества связей
    grid_stats = {}
    for qso in qso_list:
        grid = qso.gridsquare.upper().strip()
        if grid:
            if grid not in grid_stats:
                grid_stats[grid] = {
                    'count': 0,
                    'callsigns': set(),
                    'first_date': None,
                    'last_date': None
                }
            grid_stats[grid]['count'] += 1
            grid_stats[grid]['callsigns'].add(qso.callsign)
            if not grid_stats[grid]['first_date'] or qso.date < grid_stats[grid]['first_date']:
                grid_stats[grid]['first_date'] = qso.date
            if not grid_stats[grid]['last_date'] or qso.date > grid_stats[grid]['last_date']:
                grid_stats[grid]['last_date'] = qso.date

    # Преобразуем в список для сортировки
    grid_data = []
    for grid, stats in grid_stats.items():
        grid_data.append({
            'grid': grid,
            'count': stats['count'],
            'unique_callsigns': len(stats['callsigns']),
            'first_date': stats['first_date'],
            'last_date': stats['last_date'],
            'lat': None,  # Здесь можно добавить вычисление координат
            'lon': None
        })

    # Сортируем по количеству связей
    grid_data.sort(key=lambda x: x['count'], reverse=True)

    # Статистика
    total_grids = len(grid_data)
    total_qso_with_grid = sum(g['count'] for g in grid_data)
    unique_callsigns = len(set(qso.callsign for qso in qso_list))

    return render(request, 'qth_map.html', {
        'grid_data': grid_data,
        'total_grids': total_grids,
        'total_qso_with_grid': total_qso_with_grid,
        'unique_callsigns': unique_callsigns,
    })


def achievements(request):
    """
    Мои достижения - статистика и награды
    """
    import json
    from ..models import QSO, ADIFUpload
    from django.utils import timezone
    from django.template.loader import render_to_string
    from datetime import timedelta

    user = request.user

    # Обработка POST запроса с фильтрами
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            my_callsign_filter = data.get('my_callsign', '').strip()
            band_filter = data.get('band', '').strip()
            mode_filter = data.get('mode', '').strip()
            prop_mode_filter = data.get('prop_mode', '').strip()
            sat_name_filter = data.get('sat_name', '').strip()

            # Базовый QuerySet
            qso_queryset = QSO.objects.filter(user=user)

            # Применяем фильтры
            if my_callsign_filter:
                qso_queryset = qso_queryset.filter(my_callsign__iexact=my_callsign_filter)
            if band_filter:
                qso_queryset = qso_queryset.filter(band=band_filter)
            if mode_filter:
                qso_queryset = qso_queryset.filter(mode=mode_filter)
            if prop_mode_filter:
                qso_queryset = qso_queryset.filter(prop_mode=prop_mode_filter)
            if sat_name_filter:
                qso_queryset = qso_queryset.filter(sat_name=sat_name_filter)

            # Основная статистика с фильтрами
            total_qso = qso_queryset.count()

            # Статистика по диапазонам
            bands = {}
            band_order = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
            for band in band_order:
                count = qso_queryset.filter(band=band).count()
                if count > 0:
                    bands[band] = count

            # Статистика по модуляциям
            modes = {}
            mode_list = qso_queryset.values_list('mode', flat=True).distinct()
            for mode in mode_list:
                count = qso_queryset.filter(mode=mode).count()
                if count > 0:
                    modes[mode] = count

            # Уникальные позывные
            unique_callsigns = qso_queryset.values('callsign').distinct().count()

            # Страны Р-150-С
            r150s_count = qso_queryset.exclude(r150s__isnull=True).exclude(r150s='').values('r150s').distinct().count()

            # Уникальные DXCC
            dxcc_count = qso_queryset.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()

            # Уникальные регионы России
            ru_region_count = qso_queryset.exclude(ru_region__isnull=True).exclude(ru_region='').values('ru_region').distinct().count()

            # Уникальные CQ Zone
            cqz_count = qso_queryset.exclude(cqz__isnull=True).values('cqz').distinct().count()

            # Уникальные ITU Zone
            ituz_count = qso_queryset.exclude(ituz__isnull=True).values('ituz').distinct().count()

            # QTH локаторы (уникальные - первые 4 знака)
            grids_count = qso_queryset.exclude(gridsquare__isnull=True).exclude(gridsquare='').values('gridsquare').distinct().count()

            # Достижения (awards)
            achievements = []

            # 100 QSO
            if total_qso >= 100:
                achievements.append({
                    'title': 'Новичок',
                    'description': 'Зарегистрировано 100+ QSO',
                    'icon': '🎯',
                    'unlocked': True
                })

            # 500 QSO
            if total_qso >= 500:
                achievements.append({
                    'title': 'Опытный',
                    'description': 'Зарегистрировано 500+ QSO',
                    'icon': '⭐',
                    'unlocked': True
                })

            # 1000 QSO
            if total_qso >= 1000:
                achievements.append({
                    'title': 'Мастер',
                    'description': 'Зарегистрировано 1000+ QSO',
                    'icon': '🏆',
                    'unlocked': True
                })

            # 10 диапазонов
            if len(bands) >= 10:
                achievements.append({
                    'title': 'Разведчик',
                    'description': 'Связи на 10+ диапазонах',
                    'icon': '📡',
                    'unlocked': True
                })

            # 5 видов модуляции
            if len(modes) >= 5:
                achievements.append({
                    'title': 'Универсал',
                    'description': 'Связи на 5+ видах модуляции',
                    'icon': '🎛️',
                    'unlocked': True
                })

            # 50 стран Р-150-С
            if r150s_count >= 50:
                achievements.append({
                    'title': 'Охотник за DX',
                    'description': 'Связи с 50+ странами Р-150-С',
                    'icon': '🌍',
                    'unlocked': True
                })

            # 100 стран Р-150-С
            if r150s_count >= 100:
                achievements.append({
                    'title': 'Патриот',
                    'description': 'Связи со 100+ странами Р-150-С',
                    'icon': '🎖️',
                    'unlocked': True
                })

            # Формируем HTML достижений
            achievements_html = ''
            for achievement in achievements:
                achievements_html += f'''
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="achievement-card unlocked">
                        <div class="achievement-icon">{achievement['icon']}</div>
                        <div class="achievement-title">{achievement['title']}</div>
                        <div class="achievement-description">{achievement['description']}</div>
                    </div>
                </div>
                '''

            # Формируем сообщение о применённых фильтрах
            filter_parts = []
            if band_filter:
                filter_parts.append(f'диапазон {band_filter}')
            if mode_filter:
                filter_parts.append(f'вид связи {mode_filter}')
            if prop_mode_filter:
                filter_parts.append(f'prop_mode {prop_mode_filter}')
            if sat_name_filter:
                filter_parts.append(f'спутник {sat_name_filter}')

            if filter_parts:
                message = f'Отфильтровано по: {", ".join(filter_parts)}. Найдено {total_qso} QSO'
            else:
                message = f'Найдено {total_qso} QSO'

            return JsonResponse({
                'success': True,
                'total_qso': total_qso,
                'bands': bands,
                'modes': modes,
                'unique_callsigns': unique_callsigns,
                'dxcc_count': dxcc_count,
                'r150s_count': r150s_count,
                'ru_region_count': ru_region_count,
                'cqz_count': cqz_count,
                'ituz_count': ituz_count,
                'grids_count': grids_count,
                'achievements': achievements,
                'achievements_html': achievements_html,
                'message': message
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # GET запрос - обычная загрузка страницы
    # Основная статистика
    total_qso = QSO.objects.filter(user=user).count()

    # Статистика по диапазонам
    bands = {}
    band_order = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
        '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
        '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
        '2m': (144.0, 148.0), '70cm': (420.0, 450.0), '23cm': (1240.0, 1300.0),
        '13cm': (2300.0, 2450.0),
    }

    for band in band_order:
        count = QSO.objects.filter(user=user, band=band).count()
        if count > 0:
            bands[band] = count

    # Уникальные диапазоны для фильтров
    available_bands = QSO.objects.filter(user=user).values_list('band', flat=True).distinct().exclude(band__isnull=True).exclude(band='').order_by('band')

    # Статистика по модуляциям
    modes = {}
    mode_list = QSO.objects.filter(user=user).values_list('mode', flat=True).distinct()
    for mode in mode_list:
        count = QSO.objects.filter(user=user, mode=mode).count()
        if count > 0:
            modes[mode] = count

    # Уникальные позывные
    unique_callsigns = QSO.objects.filter(user=user).values('callsign').distinct().count()

    # Страны Р-150-С
    r150s_count = QSO.objects.filter(user=user).exclude(r150s__isnull=True).exclude(r150s='').values('r150s').distinct().count()

    # Уникальные DXCC
    dxcc_count = QSO.objects.filter(user=user).exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()

    # Уникальные регионы России
    ru_region_count = QSO.objects.filter(user=user).exclude(ru_region__isnull=True).exclude(ru_region='').values('ru_region').distinct().count()

    # Уникальные CQ Zone
    cqz_count = QSO.objects.filter(user=user).exclude(cqz__isnull=True).values('cqz').distinct().count()

    # Уникальные ITU Zone
    ituz_count = QSO.objects.filter(user=user).exclude(ituz__isnull=True).values('ituz').distinct().count()

    # Уникальные мои позывные
    my_callsigns = QSO.objects.filter(user=user).exclude(my_callsign__isnull=True).exclude(my_callsign='').values_list('my_callsign', flat=True).distinct().order_by('my_callsign')

    # QTH локаторы
    grids_count = QSO.objects.filter(user=user).exclude(gridsquare__isnull=True).exclude(gridsquare='').values('gridsquare').distinct().count()

    # LoTW подтверждения
    lotw_count = QSO.objects.filter(user=user, lotw='Y').count()

    # Сегодняшние связи
    today = timezone.now().date()
    today_qso = QSO.objects.filter(user=user, date=today).count()

    # Связи за последнюю неделю
    week_ago = today - timedelta(days=7)
    week_qso = QSO.objects.filter(user=user, date__gte=week_ago).count()

    # Связи за последний месяц
    month_ago = today - timedelta(days=30)
    month_qso = QSO.objects.filter(user=user, date__gte=month_ago).count()

    # Самая активная дата
    most_active_date = QSO.objects.filter(user=user).values('date').annotate(
        count=Count('id')
    ).order_by('-count').first()

    # Достижения (awards)
    achievements = []

    # 100 QSO
    if total_qso >= 100:
        achievements.append({
            'title': 'Новичок',
            'description': 'Зарегистрировано 100+ QSO',
            'icon': '🎯',
            'unlocked': True
        })

    # 500 QSO
    if total_qso >= 500:
        achievements.append({
            'title': 'Опытный',
            'description': 'Зарегистрировано 500+ QSO',
            'icon': '⭐',
            'unlocked': True
        })

    # 1000 QSO
    if total_qso >= 1000:
        achievements.append({
            'title': 'Мастер',
            'description': 'Зарегистрировано 1000+ QSO',
            'icon': '🏆',
            'unlocked': True
        })

    # 10 диапазонов
    if len(bands) >= 10:
        achievements.append({
            'title': 'Разведчик',
            'description': 'Связи на 10+ диапазонах',
            'icon': '📡',
            'unlocked': True
        })

    # 5 видов модуляции
    if len(modes) >= 5:
        achievements.append({
            'title': 'Универсал',
            'description': 'Связи на 5+ видах модуляции',
            'icon': '🎛️',
            'unlocked': True
        })

    # 50 стран Р-150-С
    if r150s_count >= 50:
        achievements.append({
            'title': 'Охотник за DX',
            'description': 'Связи с 50+ странами Р-150-С',
            'icon': '🌍',
            'unlocked': True
        })

    # 100 стран Р-150-С
    if r150s_count >= 100:
        achievements.append({
            'title': 'Патриот',
            'description': 'Связи со 100+ странами Р-150-С',
            'icon': '🎖️',
            'unlocked': True
        })

    # LoTW подтверждения
    if lotw_count >= 10:
        achievements.append({
            'title': 'Цифровой оператор',
            'description': '10+ подтверждений LoTW',
            'icon': '💻',
            'unlocked': True
        })

    # Активность за неделю
    if week_qso >= 50:
        achievements.append({
            'title': 'В эфире',
            'description': '50+ связей за неделю',
            'icon': '📻',
            'unlocked': True
        })

    return render(request, 'achievements.html', {
        'total_qso': total_qso,
        'bands': bands,
        'available_bands': list(available_bands),
        'band_order': band_order,
        'modes': modes,
        'unique_callsigns': unique_callsigns,
        'r150s_count': r150s_count,
        'dxcc_count': dxcc_count,
        'ru_region_count': ru_region_count,
        'cqz_count': cqz_count,
        'ituz_count': ituz_count,
        'grids_count': grids_count,
        'lotw_count': lotw_count,
        'today_qso': today_qso,
        'week_qso': week_qso,
        'month_qso': month_qso,
        'most_active_date': most_active_date,
        'achievements': achievements,
        'my_callsigns': list(my_callsigns),
    })


@login_required
def export_adif(request):
    """
    Экспорт лога в ADIF файл с учётом фильтров
    """
    # Получаем параметры фильтрации (те же что в logbook view)
    search_callsign = request.GET.get('search_callsign', '').strip()
    search_qth = request.GET.get('search_qth', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    mode_filter = request.GET.get('mode', '').strip()
    band_filter = request.GET.get('band', '').strip()
    sat_name_filter = request.GET.get('sat_name', '').strip()
    lotw_filter = request.GET.get('lotw', '').strip()

    # Базовый QuerySet для QSO пользователя
    qso_queryset = QSO.objects.filter(user=request.user)

    # Применяем поиск по части позывного
    if search_callsign:
        qso_queryset = qso_queryset.filter(callsign__icontains=search_callsign)

    # Применяем поиск по части QTH локатора
    if search_qth:
        qso_queryset = qso_queryset.filter(gridsquare__icontains=search_qth)

    # Фильтр по дате "с"
    if date_from:
        qso_queryset = qso_queryset.filter(date__gte=date_from)

    # Фильтр по дате "до"
    if date_to:
        qso_queryset = qso_queryset.filter(date__lte=date_to)

    # Применяем фильтры
    if mode_filter:
        qso_queryset = qso_queryset.filter(mode=mode_filter)

    # Фильтр по диапазону
    if band_filter:
        qso_queryset = qso_queryset.filter(band=band_filter)

    # Фильтр по SAT NAME
    if sat_name_filter:
        qso_queryset = qso_queryset.filter(sat_name=sat_name_filter)

    # Фильтр по LoTW
    if lotw_filter:
        qso_queryset = qso_queryset.filter(lotw=lotw_filter)

    # Сортируем по дате
    qso_queryset = qso_queryset.order_by('-date', '-time')

    # Формируем ADIF файл
    adif_content = generate_adif_content(qso_queryset)

    # Получаем позывной пользователя для имени файла
    try:
        user_callsign = request.user.radio_profile.callsign or request.user.username
    except:
        user_callsign = request.user.username

    # Формируем имя файла
    filename = f"{user_callsign}_log.adi"

    response = HttpResponse(adif_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def generate_adif_content(qso_queryset):
    """
    Генерирует содержимое ADIF файла из набора записей QSO
    """
    lines = []

    # Заголовок ADIF
    lines.append('ADIF Export from TLog')
    lines.append('Copyright 2025-2026 by Vladimir Pavlenko R3LO')
    lines.append('ADIF_VER:5 3.1.0')
    lines.append(f'PROGRAMID: TLog')
    lines.append(f'CREATED_TIMESTAMP:{datetime.now().strftime("%Y%m%d %H%M%S")}')
    lines.append('<EOH>')

    # Записи QSO
    for qso in qso_queryset:
        record_parts = []

        # Обязательные поля
        if qso.callsign:
            record_parts.append(f'<CALL:{len(qso.callsign)}>{qso.callsign}')

        if qso.date:
            date_str = qso.date.strftime('%Y%m%d')
            record_parts.append(f'<QSO_DATE:8>{date_str}')

        if qso.time:
            time_str = qso.time.strftime('%H%M%S')
            record_parts.append(f'<TIME_ON:6>{time_str}')

        if qso.my_callsign:
            record_parts.append(f'<STATION_CALLSIGN:{len(qso.my_callsign)}>{qso.my_callsign}')
            record_parts.append(f'<MY_CALLSIGN:{len(qso.my_callsign)}>{qso.my_callsign}')

        if qso.mode:
            record_parts.append(f'<MODE:{len(qso.mode)}>{qso.mode}')

        if qso.band:
            record_parts.append(f'<BAND:{len(qso.band)}>{qso.band}')

        if qso.frequency and qso.frequency > 0:
            freq_str = f"{qso.frequency:.6f}".rstrip('0').rstrip('.')
            record_parts.append(f'<FREQ:{len(freq_str)}>{freq_str}')

        if qso.rst_sent:
            record_parts.append(f'<RST_SENT:{len(qso.rst_sent)}>{qso.rst_sent}')

        if qso.rst_rcvd:
            record_parts.append(f'<RST_RCVD:{len(qso.rst_rcvd)}>{qso.rst_rcvd}')

        if qso.gridsquare:
            record_parts.append(f'<GRIDSQUARE:{len(qso.gridsquare)}>{qso.gridsquare}')

        if qso.my_gridsquare:
            record_parts.append(f'<MY_GRIDSQUARE:{len(qso.my_gridsquare)}>{qso.my_gridsquare}')

        if qso.sat_name:
            record_parts.append(f'<SAT_NAME:{len(qso.sat_name)}>{qso.sat_name}')

        if qso.prop_mode:
            record_parts.append(f'<PROP_MODE:{len(qso.prop_mode)}>{qso.prop_mode}')

        if qso.cqz:
            record_parts.append(f'<CQZ:{len(str(qso.cqz))}>{qso.cqz}')

        if qso.ituz:
            record_parts.append(f'<ITUZ:{len(str(qso.ituz))}>{qso.ituz}')

        if qso.continent:
            record_parts.append(f'<CONT:{len(qso.continent)}>{qso.continent}')

        if qso.r150s:
            record_parts.append(f'<COUNTRY:{len(qso.r150s)}>{qso.r150s}')

        if qso.lotw:
            record_parts.append(f'<LOTW_RX:{len(qso.lotw)}>{qso.lotw}')

        # Добавляем запись
        if record_parts:
            lines.append(' '.join(record_parts) + ' <EOR>')

    return '\n'.join(lines)


@login_required
def add_qso(request):
    """
    Добавление новой записи QSO
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return JsonResponse({'error': 'Ваш аккаунт заблокирован'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        import json
        from .. import r150s
        from ..region_ru import RussianRegionFinder
        import os
        from django.conf import settings
        from django.db.models import Q

        data = json.loads(request.body)

        # Получаем данные из формы (все текстовые поля преобразуются в верхний регистр)
        date_str = data.get('date')
        time_str = data.get('time')
        my_callsign = data.get('my_callsign', '').strip().upper()[:20] or request.user.username.upper()
        callsign = data.get('callsign', '').strip().upper()[:20]
        band = data.get('band', '').strip().upper()[:10] or None
        mode = (data.get('mode') or 'SSB').upper()

        # Проверка на дубликат (мой позывной, позывной корреспондента, дата, время - только часы и минуты, вид связи, диапазон)
        # Нормализуем данные для сравнения
        my_callsign_normalized = my_callsign.upper()
        callsign_normalized = callsign.upper()
        my_callsign_normalized = my_callsign.upper() if my_callsign else ''
        callsign_normalized = callsign.upper() if callsign else ''
        mode_normalized = mode.upper() if mode else 'SSB'
        band_normalized = band.upper() if band else None

        # Получаем время из запроса (формат HH:MM или HH:MM:SS)
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        # Создаем базовый запрос - сравниваем только часы и минуты (без секунд)
        duplicate_query = Q(
            user=request.user,
            my_callsign__iexact=my_callsign_normalized,
            callsign__iexact=callsign_normalized,
            date=date_str,
            mode__iexact=mode_normalized,
            time__hour=hour,
            time__minute=minute
        )

        # Добавляем диапазон если он указан
        if band_normalized:
            duplicate_query &= Q(band__iexact=band_normalized)
        else:
            duplicate_query &= Q(band__isnull=True) | Q(band='')

        duplicate_exists = QSO.objects.filter(duplicate_query).exists()

        if duplicate_exists:
            return JsonResponse({
                'error': f'QSO с {callsign_normalized} на {date_str} {hour:02d}:{minute:02d} {mode_normalized}/{band_normalized or "не указан"} уже существует'
            }, status=400)

        # Проверяем обязательные поля
        if not all([date_str, time_str, callsign, band]):
            return JsonResponse({
                'error': 'Заполните обязательные поля: дата, время, позывной, диапазон'
            }, status=400)

        # Валидация форматов
        if len(callsign) > 20:
            return JsonResponse({
                'error': 'Позывной не должен превышать 20 символов'
            }, status=400)

        frequency = data.get('frequency')
        rst_rcvd = data.get('rst_rcvd', '').upper()[:10] or None
        rst_sent = data.get('rst_sent', '').upper()[:10] or None
        my_gridsquare = data.get('my_gridsquare', '').upper()[:10] or None
        gridsquare = data.get('gridsquare', '').upper()[:10] or None
        my_qth = data.get('my_qth', '').upper()[:100] or None
        his_qth = data.get('his_qth', '').upper()[:100] or None
        sat_qso = data.get('sat_qso', 'N')
        prop_mode = data.get('prop_mode', '').upper()[:50] or None
        sat_name = data.get('sat_name', '').upper()[:50] or None
        lotw = data.get('lotw', 'N')
        paper_qsl = data.get('paper_qsl', 'N')

        # Инициализируем базы данных CTY и R150
        tlog_dir = os.path.join(settings.BASE_DIR, 'tlog')
        db_path = os.path.join(tlog_dir, 'r150cty.dat')
        cty_path = os.path.join(tlog_dir, 'cty.dat')

        r150s.init_database(db_path)
        r150s.init_cty_database(cty_path)

        # Поля SAT - только если Sat QSO отмечен
        if sat_qso == 'Y':
            sat_name = data.get('sat_name', '').upper()[:50] or None
            sat_prop_mode = data.get('prop_mode', '').upper()[:50] or None
            prop_mode = sat_prop_mode
        else:
            sat_name = None
            prop_mode = None

        # Если cqz и ituz не переданы из формы, получаем из баз данных CTY
        cqz = data.get('cqz')
        ituz = data.get('ituz')
        continent = None

        # Получаем информацию о позывном из баз данных
        if callsign:
            dxcc_info = r150s.get_dxcc_info(callsign, db_path)
            if dxcc_info:
                # Заполняем cqz, ituz и continent если не указаны в форме
                if not cqz:
                    cqz = dxcc_info.get('cq_zone')
                if not ituz:
                    ituz = dxcc_info.get('itu_zone')
                continent = dxcc_info.get('continent')

                # Получаем country из r150cty.dat (преобразуем в верхний регистр)
                r150s_country = dxcc_info.get('country')
                if r150s_country:
                    r150s_country = r150s_country.upper()[:100]

                # Получаем dxcc (primary_prefix) из cty.dat
                dxcc = r150s.get_cty_primary_prefix(callsign, cty_path)
                if dxcc:
                    dxcc = dxcc.upper()[:10]
            else:
                r150s_country = None
                dxcc = None
        else:
            r150s_country = None
            dxcc = None

        # Определяем код региона России только для российских позывных (UA, UA9, UA2)
        ru_region = None
        if callsign and dxcc:
            if dxcc.upper() in ('UA', 'UA9', 'UA2'):
                exceptions_path = os.path.join(settings.BASE_DIR, 'tlog', 'exceptions.dat')
                region_finder = RussianRegionFinder(exceptions_file=exceptions_path)
                ru_region = region_finder.get_region_code(callsign)

        # Создаем QSO
        qso = QSO.objects.create(
            user=request.user,
            my_callsign=my_callsign,
            callsign=callsign,
            date=date_str,
            time=time_str,
            band=band,
            mode=mode,
            frequency=float(frequency) if frequency else None,
            rst_rcvd=rst_rcvd,
            rst_sent=rst_sent,
            my_gridsquare=my_gridsquare,
            gridsquare=gridsquare,
            my_qth=my_qth,
            his_qth=his_qth,
            sat_name=sat_name,
            prop_mode=prop_mode,
            cqz=int(cqz) if cqz else None,
            ituz=int(ituz) if ituz else None,
            lotw=lotw,
            paper_qsl=paper_qsl,
            r150s=r150s_country if r150s_country else None,
            dxcc=dxcc if dxcc else None,
            continent=continent if continent else None,
            ru_region=ru_region
        )

        return JsonResponse({
            'success': True,
            'message': 'QSO успешно добавлено',
            'qso_id': str(qso.id)
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
