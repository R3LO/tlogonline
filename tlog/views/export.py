"""
Представления для экспорта данных
"""
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import QSO, check_user_blocked
from .helpers import generate_adif_content
@login_required
def export_adif(request):
    """
    Экспорт лога в ADIF файл с учётом фильтров
    """
    # Получаем параметры фильтрации (те же что в logbook view)
    my_callsign_filter = request.GET.get('my_callsign', '').strip()
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


