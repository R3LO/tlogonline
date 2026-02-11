"""
Представления для страницы рейтинга
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Value
from django.db.models.functions import Coalesce
from tlog.models import QSO


@login_required
def rating_page(request):
    """
    Страница рейтинга с различными категориями
    """
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    user = request.user

    # Получаем параметры фильтров
    band_type_filter = request.GET.get('band_type', 'all')  # 'all', 'hf', 'vhf', 'sat', 'qo100'
    active_tab = request.GET.get('active_tab', 'regions')  # активная вкладка
    lotw_filter = request.GET.get('lotw', 'no')  # 'yes', 'no'

    # Если активная вкладка DXCC, принудительно устанавливаем LoTW = yes
    if active_tab == 'dxcc':
        lotw_filter = 'yes'

    # КВ диапазоны
    hf_bands = ['160M', '80M', '40M', '30M', '20M', '17M', '15M', '12M', '10M']
    # УКВ диапазоны
    vhf_bands = ['6M', '2M', '70CM', '23CM', '13CM']

    # Базовый QuerySet для глобального рейтинга (все пользователи)
    global_regions_queryset = QSO.objects.filter(
        Q(r150s__in=['EUROPEAN RUSSIA', 'ASIATIC RUSSIA', 'KALININGRAD']) |
        Q(dxcc__in=['ASIATIC RUSSIA', 'EUROPEAN RUSSIA', 'KALININGRAD'])
    ).filter(
        state__isnull=False
    ).exclude(state='')

    # Применяем фильтр по типу диапазона для глобального рейтинга
    if band_type_filter == 'hf':
        global_regions_queryset = global_regions_queryset.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        global_regions_queryset = global_regions_queryset.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        global_regions_queryset = global_regions_queryset.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        global_regions_queryset = global_regions_queryset.filter(sat_name='QO-100')

    # Применяем фильтр по LoTW для глобального рейтинга
    if lotw_filter == 'yes':
        global_regions_queryset = global_regions_queryset.filter(lotw='Y')

    # Глобальный рейтинг регионов России (по всем пользователям системы)
    global_regions_stats = global_regions_queryset.values('my_callsign').annotate(
        unique_states=Count('state', distinct=True)
    ).order_by('-unique_states')

    # Глобальный рейтинг по странам Р-150-С (по всем пользователям системы)
    # Оптимизированный запрос - получаем все уникальные страны за один запрос
    global_r150s_queryset = QSO.objects.filter(
        Q(r150s__isnull=False) | Q(dxcc__isnull=False)
    ).exclude(
        r150s=''
    ).exclude(
        dxcc=''
    )

    # Применяем фильтр по типу диапазона для глобального рейтинга Р-150-С
    if band_type_filter == 'hf':
        global_r150s_queryset = global_r150s_queryset.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        global_r150s_queryset = global_r150s_queryset.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        global_r150s_queryset = global_r150s_queryset.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        global_r150s_queryset = global_r150s_queryset.filter(sat_name='QO-100')

    # Применяем фильтр по LoTW для глобального рейтинга Р-150-С
    if lotw_filter == 'yes':
        global_r150s_queryset = global_r150s_queryset.filter(lotw='Y')

    # Получаем все уникальные пары (my_callsign, r150s) и (my_callsign, dxcc) за один запрос
    # Используем values_list для оптимизации памяти
    from collections import defaultdict

    # Словарь для хранения множеств уникальных стран для каждого позывного
    callsign_countries = defaultdict(set)

    # Получаем все r150s (исключаем пустые)
    r150s_data = global_r150s_queryset.exclude(r150s='').exclude(r150s__isnull=True).values_list('my_callsign', 'r150s').distinct()
    for callsign, country in r150s_data:
        callsign_countries[callsign].add(country)

    # Получаем все dxcc (исключаем пустые)
    dxcc_data = global_r150s_queryset.exclude(dxcc='').exclude(dxcc__isnull=True).values_list('my_callsign', 'dxcc').distinct()
    for callsign, country in dxcc_data:
        callsign_countries[callsign].add(country)

    # Формируем результат
    global_r150s_stats = [
        {
            'my_callsign': callsign,
            'unique_countries': len(countries)
        }
        for callsign, countries in callsign_countries.items()
    ]

    # Сортируем по количеству уникальных стран
    global_r150s_stats.sort(key=lambda x: x['unique_countries'], reverse=True)

    # Глобальный рейтинг по странам DXCC (по всем пользователям системы)
    global_dxcc_queryset = QSO.objects.filter(
        dxcc__isnull=False
    ).exclude(dxcc='')

    # Применяем фильтр по типу диапазона для глобального рейтинга DXCC
    if band_type_filter == 'hf':
        global_dxcc_queryset = global_dxcc_queryset.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        global_dxcc_queryset = global_dxcc_queryset.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        global_dxcc_queryset = global_dxcc_queryset.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        global_dxcc_queryset = global_dxcc_queryset.filter(sat_name='QO-100')

    # Для DXCC фильтр LoTW всегда должен быть 'yes'
    global_dxcc_queryset = global_dxcc_queryset.filter(lotw='Y')

    # Глобальный рейтинг DXCC по всем пользователям системы
    global_dxcc_stats = global_dxcc_queryset.values('my_callsign').annotate(
        unique_dxcc=Count('dxcc', distinct=True)
    ).order_by('-unique_dxcc')

    # Получаем все QSO пользователя
    qso_queryset = QSO.objects.filter(user=user)

    # 1. Регионы России
    # Фильтруем QSO из России (r150s или dxcc с RU)
    russia_qso = qso_queryset.filter(
        Q(r150s__in=['EUROPEAN RUSSIA', 'ASIATIC RUSSIA', 'KALININGRAD']) |
        Q(dxcc__in=['ASIATIC RUSSIA', 'EUROPEAN RUSSIA', 'KALININGRAD'])
    ).filter(
        state__isnull=False
    ).exclude(state='')

    # Применяем фильтр по типу диапазона
    if band_type_filter == 'hf':
        russia_qso = russia_qso.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        russia_qso = russia_qso.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        russia_qso = russia_qso.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        russia_qso = russia_qso.filter(sat_name='QO-100')

    # Применяем фильтр по LoTW
    if lotw_filter == 'yes':
        russia_qso = russia_qso.filter(lotw='Y')

    regions_stats = russia_qso.values('state').annotate(
        count=Count('id')
    ).order_by('-count')

    # 2. Страны Р-150-С
    r150s_qso = qso_queryset.filter(
        r150s__isnull=False
    ).exclude(r150s='')

    # Применяем фильтр по типу диапазона
    if band_type_filter == 'hf':
        r150s_qso = r150s_qso.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        r150s_qso = r150s_qso.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        r150s_qso = r150s_qso.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        r150s_qso = r150s_qso.filter(sat_name='QO-100')

    # Применяем фильтр по LoTW
    if lotw_filter == 'yes':
        r150s_qso = r150s_qso.filter(lotw='Y')

    r150s_stats = r150s_qso.values('r150s').annotate(
        count=Count('id')
    ).order_by('-count')

    # 3. Страны DXCC
    dxcc_qso = qso_queryset.filter(
        dxcc__isnull=False
    ).exclude(dxcc='')

    # Применяем фильтр по типу диапазона
    if band_type_filter == 'hf':
        dxcc_qso = dxcc_qso.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        dxcc_qso = dxcc_qso.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        dxcc_qso = dxcc_qso.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        dxcc_qso = dxcc_qso.filter(sat_name='QO-100')

    # Применяем фильтр по LoTW
    if lotw_filter == 'yes':
        dxcc_qso = dxcc_qso.filter(lotw='Y')

    dxcc_stats = dxcc_qso.values('dxcc').annotate(
        count=Count('id')
    ).order_by('-count')

    # 4. QTH локаторы
    qth_qso = qso_queryset.filter(
        gridsquare__isnull=False
    ).exclude(gridsquare='')

    # Применяем фильтр по типу диапазона
    if band_type_filter == 'hf':
        qth_qso = qth_qso.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        qth_qso = qth_qso.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        qth_qso = qth_qso.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        qth_qso = qth_qso.filter(sat_name='QO-100')

    # Применяем фильтр по LoTW
    if lotw_filter == 'yes':
        qth_qso = qth_qso.filter(lotw='Y')

    qth_stats = qth_qso.values('gridsquare').annotate(
        count=Count('id')
    ).order_by('-count')

    # 5. Уникальные позывные
    callsigns_qso = qso_queryset

    # Применяем фильтр по типу диапазона
    if band_type_filter == 'hf':
        callsigns_qso = callsigns_qso.filter(band__in=hf_bands)
    elif band_type_filter == 'vhf':
        callsigns_qso = callsigns_qso.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
    elif band_type_filter == 'sat':
        callsigns_qso = callsigns_qso.filter(prop_mode='SAT')
    elif band_type_filter == 'qo100':
        callsigns_qso = callsigns_qso.filter(sat_name='QO-100')

    # Применяем фильтр по LoTW
    if lotw_filter == 'yes':
        callsigns_qso = callsigns_qso.filter(lotw='Y')

    callsigns_stats = callsigns_qso.values('callsign').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'global_regions_stats': global_regions_stats,
        'global_r150s_stats': global_r150s_stats,
        'global_dxcc_stats': global_dxcc_stats,
        'regions_stats': regions_stats,
        'r150s_stats': r150s_stats,
        'dxcc_stats': dxcc_stats,
        'qth_stats': qth_stats,
        'callsigns_stats': callsigns_stats,
        'band_type_filter': band_type_filter,
        'lotw_filter': lotw_filter,
    }

    return render(request, 'rating_base.html', context)
