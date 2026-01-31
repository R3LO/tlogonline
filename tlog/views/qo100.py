# Функции QO-100 рейтингов

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from ..models import QSO, check_user_blocked
from tlog.region_ru import RussianRegionFinder
from tlog.r150s import DXCCDatabase, CTYDatabase
import os


@login_required
def qo100_regions(request):
    """
    Страница рейтинга QO-100 - регионы России
    Показывает статистику по регионам РФ для всех QSO с lotw = 'Y'
    """
    from tlog.region_ru import RussianRegionFinder

    region_finder = RussianRegionFinder()

    # Получаем уникальные пары my_callsign + регион + callsign для QSO с lotw = 'Y'
    qso_filtered = QSO.objects.filter(
        lotw='Y',
        ru_region__isnull=False
    ).exclude(ru_region='').values('my_callsign', 'ru_region', 'callsign').distinct()

    # Группируем по my_callsign, затем по региону
    from collections import defaultdict
    callsign_data = defaultdict(lambda: defaultdict(set))

    for item in qso_filtered:
        my_call = item['my_callsign']
        region_code = item['ru_region']
        call = item['callsign']
        callsign_data[my_call][region_code].add(call)

    # Формируем список с позывным, количеством и данными регионов
    ratings = []
    for my_call, regions_dict in callsign_data.items():
        regions_list = []
        for region_code, callsigns in regions_dict.items():
            region_name = region_finder.region_data.get(region_code, region_code)
            regions_list.append({
                'code': region_code,
                'name': region_name,
                'callsigns': sorted(list(callsigns))
            })
        # Сортируем по названию региона
        regions_list.sort(key=lambda x: x['name'])

        ratings.append({
            'callsign': my_call,
            'count': len(regions_list),
            'regions': regions_list
        })

    # Сортируем по количеству (убывание), затем по позывному
    ratings.sort(key=lambda x: (-x['count'], x['callsign']))

    return render(request, 'qo100/regions.html', {
        'ratings': ratings,
        'page_title': 'Регионы России QO-100',
        'page_subtitle': 'По регионам РФ, подтвержденным в LoTW',
    })


@login_required
def qo100_r150s(request):
    """
    Страница рейтинга QO-100 - страны Р-150-С
    Показывает статистику по странам для всех QSO с lotw = 'Y'
    """
    from tlog.r150s import DXCCDatabase
    import os

    # Загружаем базу данных R150
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'r150cty.dat')
    dxcc_db = DXCCDatabase(db_path)

    # Создаем словарь код -> название страны
    country_names = {}
    for entry in dxcc_db.entries:
        # Проверяем все префиксы, чтобы найти нужный код
        for prefix in entry.prefixes:
            # Код r150s может быть в формате "=P" или просто префикс
            if '=' in prefix:
                code = prefix.split('=')[1].strip()
                country_names[code] = entry.name

    # Получаем уникальные пары my_callsign + r150s для QSO с lotw = 'Y'
    qso_filtered = QSO.objects.filter(
        lotw='Y',
        r150s__isnull=False
    ).exclude(r150s='').values('my_callsign', 'r150s', 'callsign').distinct()

    # Группируем по my_callsign, затем по стране
    from collections import defaultdict
    callsign_data = defaultdict(lambda: defaultdict(set))

    for item in qso_filtered:
        my_call = item['my_callsign']
        country_code = item['r150s']
        call = item['callsign']
        callsign_data[my_call][country_code].add(call)

    # Формируем список с позывным, количеством и данными стран
    ratings = []
    for my_call, countries_dict in callsign_data.items():
        countries_list = []
        for country_code, callsigns in countries_dict.items():
            country_name = country_names.get(country_code, country_code)
            countries_list.append({
                'code': country_code,
                'name': country_name,
                'callsigns': sorted(list(callsigns))
            })
        # Сортируем по названию страны
        countries_list.sort(key=lambda x: x['name'])

        ratings.append({
            'callsign': my_call,
            'count': len(countries_list),
            'countries': countries_list
        })

    # Сортируем по количеству (убывание), затем по позывному
    ratings.sort(key=lambda x: (-x['count'], x['callsign']))

    return render(request, 'qo100/r150s.html', {
        'ratings': ratings,
        'page_title': 'Страны Р-150-С QO-100',
        'page_subtitle': 'По странам Р-150-С, подтвержденным в LoTW',
    })


@login_required
def qo100_grids(request):
    """
    Страница рейтинга QO-100 - локаторы
    Показывает статистику по локаторам для всех QSO с lotw = 'Y'
    """
    # Получаем уникальные пары my_callsign + gridsquare для QSO с lotw = 'Y'
    qso_filtered = QSO.objects.filter(
        lotw='Y',
        gridsquare__isnull=False
    ).exclude(gridsquare='').values('my_callsign', 'gridsquare', 'callsign').distinct()

    # Группируем по my_callsign, затем по локатору (первые 4 знака)
    from collections import defaultdict
    callsign_data = defaultdict(lambda: defaultdict(set))

    for item in qso_filtered:
        my_call = item['my_callsign']
        # Берем только первые 4 знака локатора
        grid_full = item['gridsquare']
        grid_short = grid_full[:4] if len(grid_full) >= 4 else grid_full
        call = item['callsign']
        callsign_data[my_call][grid_short].add(call)

    # Формируем список с позывным, количеством и данными локаторов
    ratings = []
    for my_call, grids_dict in callsign_data.items():
        grids_list = []
        for grid_code, callsigns in grids_dict.items():
            grids_list.append({
                'code': grid_code,
                'callsigns': sorted(list(callsigns))
            })
        # Сортируем по коду локатора
        grids_list.sort(key=lambda x: x['code'])

        ratings.append({
            'callsign': my_call,
            'count': len(grids_list),
            'grids': grids_list
        })

    # Сортируем по количеству (убывание), затем по позывному
    ratings.sort(key=lambda x: (-x['count'], x['callsign']))

    return render(request, 'qo100/grids.html', {
        'ratings': ratings,
        'page_title': 'Локаторы QO-100',
        'page_subtitle': 'По локаторам, подтвержденным в LoTW',
    })


@login_required
def qo100_unique_callsigns(request):
    """
    Страница рейтинга QO-100 - уникальные позывные
    Показывает статистику по уникальным позывным для всех QSO с lotw = 'Y'
    """
    # Получаем уникальные пары my_callsign + callsign для QSO с lotw = 'Y'
    qso_filtered = QSO.objects.filter(
        lotw='Y',
        callsign__isnull=False
    ).exclude(callsign='').values('my_callsign', 'callsign').distinct()

    # Группируем по my_callsign и собираем уникальные позывные
    from collections import defaultdict
    callsign_data = defaultdict(list)

    for item in qso_filtered:
        my_call = item['my_callsign']
        call = item['callsign']
        if call not in callsign_data[my_call]:
            callsign_data[my_call].append(call)

    # Формируем список с позывным и списком уникальных корреспондентов
    ratings = []
    for my_call, callsigns in callsign_data.items():
        ratings.append({
            'callsign': my_call,
            'count': len(callsigns),
            'unique_callsigns': sorted(callsigns)  # Сортировка по алфавиту
        })

    # Сортируем по количеству (убывание), затем по позывному
    ratings.sort(key=lambda x: (-x['count'], x['callsign']))

    return render(request, 'qo100/unique_callsigns.html', {
        'ratings': ratings,
        'page_title': 'Уникальные позывные QO-100',
        'page_subtitle': 'По уникальным позывным, подтвержденным в LoTW',
    })


@login_required
def qo100_dxcc(request):
    """
    Страница рейтинга QO-100 - страны DXCC
    Показывает статистику по странам DXCC для всех QSO с lotw = 'Y'
    """
    from tlog.r150s import CTYDatabase
    import os

    # Загружаем базу данных CTY
    cty_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cty.dat')
    cty_db = CTYDatabase(cty_path)

    # Создаем словарь код (primary_prefix) -> название страны
    country_names = {}
    for entry in cty_db.entries:
        primary_prefix = entry.primary_prefix
        if primary_prefix:
            country_names[primary_prefix] = entry.name

    # Получаем уникальные пары my_callsign + dxcc + callsign для QSO с lotw = 'Y'
    qso_filtered = QSO.objects.filter(
        lotw='Y',
        dxcc__isnull=False
    ).exclude(dxcc='').values('my_callsign', 'dxcc', 'callsign').distinct()

    # Группируем по my_callsign, затем по стране DXCC
    from collections import defaultdict
    callsign_data = defaultdict(lambda: defaultdict(set))

    for item in qso_filtered:
        my_call = item['my_callsign']
        dxcc_code = item['dxcc']
        call = item['callsign']
        callsign_data[my_call][dxcc_code].add(call)

    # Формируем список с позывным, количеством и данными стран
    ratings = []
    for my_call, countries_dict in callsign_data.items():
        countries_list = []
        for country_code, callsigns in countries_dict.items():
            country_name = country_names.get(country_code, country_code)
            countries_list.append({
                'code': country_code,
                'name': country_name,
                'callsigns': sorted(list(callsigns))
            })
        # Сортируем по названию страны
        countries_list.sort(key=lambda x: x['name'])

        ratings.append({
            'callsign': my_call,
            'count': len(countries_list),
            'countries': countries_list
        })

    # Сортируем по количеству (убывание), затем по позывному
    ratings.sort(key=lambda x: (-x['count'], x['callsign']))

    return render(request, 'qo100/dxcc.html', {
        'ratings': ratings,
        'page_title': 'Страны DXCC QO-100',
        'page_subtitle': 'По странам DXCC, подтвержденным в LoTW',
    })