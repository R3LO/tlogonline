"""
Представления для работы с журналом QSO
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from ..models import QSO, RadioProfile, ADIFUpload


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
            Q(callsign__icontains=search_query) | Q(gridsquare__icontains=search_query)
        )

    # Применяем фильтры
    if callsign_filter:
        qso_queryset = qso_queryset.filter(callsign__icontains=callsign_filter)

    if qth_filter:
        qso_queryset = qso_queryset.filter(gridsquare__icontains=qth_filter)

    if mode_filter:
        qso_queryset = qso_queryset.filter(mode=mode_filter)

    if band_filter:
        band_ranges = {
            '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
            '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
            '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
            '4m': (70.0, 70.5), '2m': (144.0, 148.0), '70cm': (420.0, 450.0),
            '23cm': (1240.0, 1300.0), '13cm': (2400.0, 2500.0),
        }
        if band_filter in band_ranges:
            min_freq, max_freq = band_ranges[band_filter]
            qso_queryset = qso_queryset.filter(frequency__gte=min_freq, frequency__lte=max_freq)

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

    # Статистика для выбранных фильтров
    filtered_stats = {
        'total_qso': total_count,
        'unique_callsigns': qso_queryset.values('callsign').distinct().count(),
        'unique_qth': qso_queryset.filter(gridsquare__isnull=False).exclude(gridsquare='').values('gridsquare').distinct().count(),
        'unique_modes': len(unique_modes),
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
        'search_query': search_query,
        'callsign_filter': callsign_filter,
        'qth_filter': qth_filter,
        'mode_filter': mode_filter,
        'band_filter': band_filter,
        'available_modes': unique_modes,
        'available_bands': list(band_stats.keys()),
        'filtered_stats': filtered_stats,
        'band_stats': band_stats,
        'get_band_from_frequency': get_band_from_frequency,
    }

    return render(request, 'logbook.html', context)


def logbook_search(request, callsign):
    """
    Поиск по логам пользователя по позывному.
    """
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
    context = {'callsign': callsign, 'has_logs': True, 'search_callsign': search_callsign, 'qso_list': None}

    if search_callsign:
        qso_queryset = QSO.objects.filter(
            my_callsign=callsign,
            callsign__icontains=search_callsign
        ).order_by('-date', '-time')

        total_qso = qso_queryset.count()
        unique_callsigns = qso_queryset.values('callsign').distinct().count()

        # Статистика по диапазонам
        band_stats = {}
        bands = ['160m', '80m', '40m', '20m', '15m', '10m', '6m', '2m', '70cm']
        band_ranges = {
            '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '20m': (14.0, 14.35),
            '15m': (21.0, 21.45), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
            '2m': (144.0, 148.0), '70cm': (420.0, 450.0),
        }

        for band in bands:
            if band in band_ranges:
                min_freq, max_freq = band_ranges[band]
                count = qso_queryset.filter(frequency__gte=min_freq, frequency__lte=max_freq).count()
                if count > 0:
                    band_stats[band] = count

        context.update({
            'qso_list': qso_queryset,
            'total_qso': total_qso,
            'unique_callsigns': unique_callsigns,
            'band_stats': band_stats,
        })

    return render(request, 'logbook_search.html', context)


def clear_logbook(request):
    """
    Удаляет все записи QSO и загруженные ADIF файлы пользователя
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Подсчитываем количество записей для статистики
        qso_count = QSO.objects.filter(user=request.user).count()
        unique_callsigns = QSO.objects.filter(user=request.user).values('callsign').distinct().count()
        unique_qth = QSO.objects.filter(user=request.user).filter(
            gridsquare__isnull=False
        ).exclude(gridsquare='').values('gridsquare').distinct().count()
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
                'unique_qth': unique_qth
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при удалении записей: {str(e)}'
        }, status=500)