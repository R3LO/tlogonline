"""
Представления для страницы рейтинга
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
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

    regions_stats = russia_qso.values('state').annotate(
        count=Count('id')
    ).order_by('-count')

    # 2. Страны Р-150-С
    r150s_stats = qso_queryset.filter(
        r150s__isnull=False
    ).exclude(r150s='').values('r150s').annotate(
        count=Count('id')
    ).order_by('-count')

    # 3. Страны DXCC
    dxcc_stats = qso_queryset.filter(
        dxcc__isnull=False
    ).exclude(dxcc='').values('dxcc').annotate(
        count=Count('id')
    ).order_by('-count')

    # 4. QTH локаторы
    qth_stats = qso_queryset.filter(
        gridsquare__isnull=False
    ).exclude(gridsquare='').values('gridsquare').annotate(
        count=Count('id')
    ).order_by('-count')

    # 5. Уникальные позывные
    callsigns_stats = qso_queryset.values('callsign').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'regions_stats': regions_stats,
        'r150s_stats': r150s_stats,
        'dxcc_stats': dxcc_stats,
        'qth_stats': qth_stats,
        'callsigns_stats': callsigns_stats,
    }

    return render(request, 'rating_base.html', context)
