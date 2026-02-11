"""
Представления для страницы logbook
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from datetime import datetime, time
from django.contrib import messages
from ..models import QSO, RadioProfile, ADIFUpload, check_user_blocked
from .helpers import get_band_from_frequency
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
    if request.method == 'POST':
        my_callsign_filter = request.POST.get('my_callsign', '').strip()
        search_callsign = request.POST.get('search_callsign', '').strip()
        search_qth = request.POST.get('search_qth', '').strip()
        date_from = request.POST.get('date_from', '').strip()
        date_to = request.POST.get('date_to', '').strip()
        mode_filter = request.POST.get('mode', '').strip()
        band_filter = request.POST.get('band', '').strip()
        sat_name_filter = request.POST.get('sat_name', '').strip()
        lotw_filter = request.POST.get('lotw', '').strip()
    else:
        # GET запрос - берем из параметров URL или из кук
        my_callsign_filter = request.GET.get('my_callsign', '').strip() or request.COOKIES.get('logbook_filter_my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip() or request.COOKIES.get('logbook_filter_search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip() or request.COOKIES.get('logbook_filter_search_qth', '').strip()
        date_from = request.GET.get('date_from', '').strip() or request.COOKIES.get('logbook_filter_date_from', '').strip()
        date_to = request.GET.get('date_to', '').strip() or request.COOKIES.get('logbook_filter_date_to', '').strip()
        mode_filter = request.GET.get('mode', '').strip() or request.COOKIES.get('logbook_filter_mode', '').strip()
        band_filter = request.GET.get('band', '').strip() or request.COOKIES.get('logbook_filter_band', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip() or request.COOKIES.get('logbook_filter_sat_name', '').strip()
        lotw_filter = request.GET.get('lotw', '').strip() or request.COOKIES.get('logbook_filter_lotw', '').strip()

    # Базовый QuerySet для QSO пользователя
    qso_queryset = QSO.objects.filter(user=request.user)

    # Фильтр по моему позывному
    if my_callsign_filter:
        qso_queryset = qso_queryset.filter(my_callsign__iexact=my_callsign_filter)

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
    page = int(request.POST.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size

    qso_list = qso_queryset[start:end]
    total_count = qso_queryset.count()
    total_pages = (total_count + page_size - 1) // page_size

    # Уникальные значения для фильтров
    unique_modes = qso_queryset.values_list('mode', flat=True).distinct().order_by('mode')
    unique_bands = qso_queryset.values_list('band', flat=True).distinct().exclude(band__isnull=True).exclude(band='').order_by('band')
    unique_sat_names = qso_queryset.values_list('sat_name', flat=True).distinct().exclude(sat_name__isnull=True).exclude(sat_name='').order_by('sat_name')

    # Уникальные мои позывные для фильтра
    my_callsigns = list(QSO.objects.filter(user=request.user, my_callsign__isnull=False, my_callsign__gt='')
                       .values_list('my_callsign', flat=True).distinct().order_by('my_callsign'))

    # Статистика для выбранных фильтров
    filtered_stats = {
        'total_qso': total_count,
        'unique_callsigns': qso_queryset.values('callsign').distinct().count(),
        'unique_dxcc': qso_queryset.filter(dxcc__isnull=False).exclude(dxcc='').values('dxcc').distinct().count(),
        'unique_r150s': qso_queryset.filter(r150s__isnull=False).exclude(r150s='').values('r150s').distinct().count(),
        'unique_states': qso_queryset.filter(
            Q(r150s__in=['EUROPEAN RUSSIA', 'ASIATIC RUSSIA', 'KALININGRAD']) |
            Q(dxcc__in=['ASIATIC RUSSIA', 'EUROPEAN RUSSIA', 'KALININGRAD']),
            state__isnull=False
        ).exclude(state='').values('state').distinct().count(),
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

    # Получаем загруженные ADIF файлы для сайдбара
    adif_uploads = ADIFUpload.objects.filter(user=request.user).order_by('-upload_date')[:10]

    # Диплом Cosmos - уникальные callsign для спутниковых QSO (без учета фильтров)
    cosmos_qso = QSO.objects.filter(
        user=request.user
    ).filter(
        Q(prop_mode='SAT') | Q(band='13CM')
    )
    cosmos_unique_callsigns = cosmos_qso.values('callsign').distinct().count()

    context = {
        'user': request.user,
        'user_callsign': user_callsign,
        'qso_list': qso_list,
        'total_count': total_count,
        'unique_callsigns': filtered_stats.get('unique_callsigns', 0),
        'current_page': page,
        'total_pages': total_pages,
        'page_size': page_size,
        'my_callsign_filter': my_callsign_filter,
        'search_callsign': search_callsign,
        'search_qth': search_qth,
        'date_from': date_from,
        'date_to': date_to,
        'mode_filter': mode_filter,
        'band_filter': band_filter,
        'sat_name_filter': sat_name_filter,
        'lotw_filter': lotw_filter,
        'my_callsigns': my_callsigns,
        'available_modes': unique_modes,
        'available_bands': unique_bands,
        'available_sat_names': unique_sat_names,
        'filtered_stats': filtered_stats,
        'band_stats': band_stats,
        'get_band_from_frequency': get_band_from_frequency,
        'adif_uploads': adif_uploads,
        'cosmos_unique_callsigns': cosmos_unique_callsigns,
    }

    return render(request, 'logbook_base.html', context)


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

