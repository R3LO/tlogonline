"""
Представления для карты QTH
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import QSO, check_user_blocked


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


