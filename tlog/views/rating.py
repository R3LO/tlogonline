"""
Представления для страницы рейтинга (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Value
from django.db.models.functions import Coalesce, Substr
from django.core.cache import cache
from tlog.models import QSO
from collections import defaultdict


@login_required
def rating_page(request):
    """
    Страница рейтинга с различными категориями (ОПТИМИЗИРОВАННАЯ)
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

    # Формируем ключ кэша на основе фильтров (кэшируем глобальные рейтинги на 10 минут)
    cache_key = f'rating_global_{band_type_filter}_{lotw_filter}'
    cached_global_stats = cache.get(cache_key)

    if cached_global_stats:
        # Если данные в кэше, используем их
        (global_regions_stats, global_r150s_stats, global_dxcc_stats,
         global_callsigns_stats, global_cqz_stats, global_ituz_stats,
         global_iota_stats, global_qth_stats) = cached_global_stats
    else:
        # Базовый фильтр по диапазону и LoTW для всех глобальных запросов
        base_filters = Q()

        if band_type_filter == 'hf':
            base_filters &= Q(band__in=hf_bands)
        elif band_type_filter == 'vhf':
            base_filters &= Q(band__in=vhf_bands) & ~Q(prop_mode='SAT')
        elif band_type_filter == 'sat':
            base_filters &= Q(prop_mode='SAT')
        elif band_type_filter == 'qo100':
            base_filters &= Q(sat_name='QO-100')

        if lotw_filter == 'yes':
            base_filters &= Q(lotw='Y')

        # 1. Глобальный рейтинг регионов России
        global_regions_stats = QSO.objects.filter(
            base_filters &
            (Q(r150s__in=['EUROPEAN RUSSIA', 'ASIATIC RUSSIA', 'KALININGRAD']) |
             Q(dxcc__in=['ASIATIC RUSSIA', 'EUROPEAN RUSSIA', 'KALININGRAD'])) &
            Q(state__isnull=False) & ~Q(state='')
        ).values('user__username').annotate(
            unique_states=Count('state', distinct=True)
        ).order_by('-unique_states')[:100]  # Ограничиваем топ-100

        # 2. Глобальный рейтинг по странам Р-150-С (оптимизировано)
        # Получаем уникальные r150s и dxcc за один запрос
        r150s_dxcc_data = QSO.objects.filter(
            base_filters &
            (Q(r150s__isnull=False, r150s__gt='') | Q(dxcc__isnull=False, dxcc__gt=''))
        ).values_list('user__username', 'r150s', 'dxcc').distinct()

        username_countries = defaultdict(set)
        for username, r150s, dxcc in r150s_dxcc_data:
            if r150s:
                username_countries[username].add(r150s)
            if dxcc:
                username_countries[username].add(dxcc)

        global_r150s_stats = [
            {'username': username, 'unique_countries': len(countries)}
            for username, countries in username_countries.items()
        ]
        global_r150s_stats.sort(key=lambda x: x['unique_countries'], reverse=True)
        global_r150s_stats = global_r150s_stats[:100]  # Ограничиваем топ-100

        # 3. Глобальный рейтинг по DXCC (LoTW всегда yes)
        dxcc_filter = base_filters
        if lotw_filter != 'yes':
            dxcc_filter &= Q(lotw='Y')

        global_dxcc_stats = QSO.objects.filter(
            dxcc_filter & Q(dxcc__isnull=False) & ~Q(dxcc='')
        ).values('user__username').annotate(
            unique_dxcc=Count('dxcc', distinct=True)
        ).order_by('-unique_dxcc')[:100]

        # 4. Глобальный рейтинг по уникальным позывным
        global_callsigns_stats = QSO.objects.filter(
            base_filters & Q(callsign__isnull=False) & ~Q(callsign='')
        ).values('user__username').annotate(
            unique_callsigns=Count('callsign', distinct=True)
        ).order_by('-unique_callsigns')[:100]

        # 5. Глобальный рейтинг по CQ зонам
        global_cqz_stats = QSO.objects.filter(
            base_filters & Q(cqz__gt=0)
        ).values('user__username').annotate(
            unique_cqz=Count('cqz', distinct=True)
        ).order_by('-unique_cqz')[:100]

        # 6. Глобальный рейтинг по ITU зонам
        global_ituz_stats = QSO.objects.filter(
            base_filters & Q(ituz__gt=0)
        ).values('user__username').annotate(
            unique_ituz=Count('ituz', distinct=True)
        ).order_by('-unique_ituz')[:100]

        # 7. Глобальный рейтинг по IOTA
        global_iota_stats = QSO.objects.filter(
            base_filters & Q(iota__isnull=False) & ~Q(iota='')
        ).values('user__username').annotate(
            unique_iota=Count('iota', distinct=True)
        ).order_by('-unique_iota')[:100]

        # 8. Глобальный рейтинг по QTH локаторам (оптимизировано)
        qth_data = QSO.objects.filter(
            base_filters & (Q(gridsquare__isnull=False) | Q(vucc_grids__isnull=False))
        ).exclude(Q(gridsquare='') & Q(vucc_grids='')).values_list(
            'user__username', 'gridsquare', 'vucc_grids'
        )

        username_grids = defaultdict(set)
        for username, gridsquare, vucc_grids in qth_data:
            if gridsquare and len(gridsquare) >= 4:
                grid_4 = gridsquare[:4].upper()
                if grid_4:
                    username_grids[username].add(grid_4)
            if vucc_grids:
                for grid in vucc_grids.split(','):
                    grid = grid.strip()
                    if grid and len(grid) >= 4:
                        grid_4 = grid[:4].upper()
                        if grid_4:
                            username_grids[username].add(grid_4)

        global_qth_stats = [
            {'username': username, 'unique_grids': len(grids)}
            for username, grids in username_grids.items()
        ]
        global_qth_stats.sort(key=lambda x: x['unique_grids'], reverse=True)
        global_qth_stats = global_qth_stats[:100]

        # Сохраняем в кэш на 10 минут
        cache.set(cache_key, (
            global_regions_stats, global_r150s_stats, global_dxcc_stats,
            global_callsigns_stats, global_cqz_stats, global_ituz_stats,
            global_iota_stats, global_qth_stats
        ), 600)

    # Кэшируем личную статистику пользователя (на 5 минут)
    personal_cache_key = f'rating_personal_{user.id}_{band_type_filter}_{lotw_filter}'
    cached_personal_stats = cache.get(personal_cache_key)

    if cached_personal_stats:
        (regions_stats, r150s_stats, dxcc_stats,
         qth_stats, callsigns_stats) = cached_personal_stats
    else:
        # Получаем все QSO пользователя с фильтрами
        qso_queryset = QSO.objects.filter(user=user)

        # Применяем фильтры к пользовательским запросам
        if band_type_filter == 'hf':
            qso_queryset = qso_queryset.filter(band__in=hf_bands)
        elif band_type_filter == 'vhf':
            qso_queryset = qso_queryset.filter(band__in=vhf_bands).exclude(prop_mode='SAT')
        elif band_type_filter == 'sat':
            qso_queryset = qso_queryset.filter(prop_mode='SAT')
        elif band_type_filter == 'qo100':
            qso_queryset = qso_queryset.filter(sat_name='QO-100')

        if lotw_filter == 'yes':
            qso_queryset = qso_queryset.filter(lotw='Y')

        # 1. Регионы России
        russia_qso = qso_queryset.filter(
            (Q(r150s__in=['EUROPEAN RUSSIA', 'ASIATIC RUSSIA', 'KALININGRAD']) |
             Q(dxcc__in=['ASIATIC RUSSIA', 'EUROPEAN RUSSIA', 'KALININGRAD'])) &
            Q(state__isnull=False) & ~Q(state='')
        )

        regions_stats = russia_qso.values('state').annotate(
            count=Count('id')
        ).order_by('-count')

        # 2. Страны Р-150-С
        r150s_stats = qso_queryset.filter(
            r150s__isnull=False, r150s__gt=''
        ).values('r150s').annotate(
            count=Count('id')
        ).order_by('-count')

        # 3. Страны DXCC
        dxcc_stats = qso_queryset.filter(
            dxcc__isnull=False, dxcc__gt=''
        ).values('dxcc').annotate(
            count=Count('id')
        ).order_by('-count')

        # 4. QTH локаторы
        qth_stats = qso_queryset.filter(
            gridsquare__isnull=False, gridsquare__gt=''
        ).values('gridsquare').annotate(
            count=Count('id')
        ).order_by('-count')

        # 5. Уникальные позывные
        callsigns_stats = qso_queryset.filter(
            callsign__isnull=False, callsign__gt=''
        ).values('callsign').annotate(
            count=Count('id')
        ).order_by('-count')

        # Сохраняем в кэш на 5 минут
        cache.set(personal_cache_key, (
            regions_stats, r150s_stats, dxcc_stats,
            qth_stats, callsigns_stats
        ), 300)

    context = {
        'global_regions_stats': global_regions_stats,
        'global_r150s_stats': global_r150s_stats,
        'global_dxcc_stats': global_dxcc_stats,
        'global_callsigns_stats': global_callsigns_stats,
        'global_cqz_stats': global_cqz_stats,
        'global_ituz_stats': global_ituz_stats,
        'global_iota_stats': global_iota_stats,
        'global_qth_stats': global_qth_stats,
        'regions_stats': regions_stats,
        'r150s_stats': r150s_stats,
        'dxcc_stats': dxcc_stats,
        'qth_stats': qth_stats,
        'callsigns_stats': callsigns_stats,
        'band_type_filter': band_type_filter,
        'lotw_filter': lotw_filter,
    }

    return render(request, 'rating_base.html', context)
