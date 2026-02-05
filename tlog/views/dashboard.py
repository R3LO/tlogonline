# Функции личного кабинета (dashboard)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date, time
from django.db.utils import IntegrityError
import os
from django.conf import settings
from ..models import QSO, RadioProfile, ADIFUpload, check_user_blocked
from tlog import r150s
from tlog.region_ru import RussianRegionFinder


def dashboard(request):
    """
    Личный кабинет радиолюбителя
    """
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    # Обработка формы ручного ввода QSO
    if request.method == 'POST' and request.POST.get('action') == 'add_qso':
        return handle_add_qso(request)

    # Получаем профиль радиолюбителя
    try:
        profile = request.user.radio_profile
    except RadioProfile.DoesNotExist:
        profile = None

    # Получаем QSO пользователя
    user_qso = QSO.objects.filter(user=request.user)

    # Подсчитываем статистику
    total_qso = user_qso.count()
    unique_callsigns = user_qso.values('callsign').distinct().count()

    # Статистика по DXCC (страны)
    dxcc_count = user_qso.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()

    # Статистика по Р-150-С (регионы России)
    r150s_count = user_qso.exclude(r150s__isnull=True).exclude(r150s='').values('r150s').distinct().count()

    # Статистика по регионам России (state)
    state_count = user_qso.exclude(state__isnull=True).exclude(state='').values('state').distinct().count()

    # Статистика по видам модуляции
    mode_stats = {}
    mode_choices = dict(QSO._meta.get_field('mode').choices)
    for mode in mode_choices.keys():
        count = user_qso.filter(mode=mode).count()
        if count > 0:
            mode_stats[mode] = count

    # Последние QSO (последние 10)
    recent_qso = user_qso.order_by('-date', '-time')[:10]

    # Получаем загруженные ADIF файлы
    adif_uploads = ADIFUpload.objects.filter(user=request.user).order_by('-upload_date')[:10]

    context = {
        'user': request.user,
        'profile': profile,
        'total_qso': total_qso,
        'unique_callsigns': unique_callsigns,
        'dxcc_count': dxcc_count,
        'r150s_count': r150s_count,
        'state_count': state_count,
        'recent_qso': recent_qso,
        'mode_statistics': mode_stats,
        'adif_uploads': adif_uploads,
        'cqz_count': user_qso.exclude(cqz__isnull=True).values('cqz').distinct().count(),
        'ituz_count': user_qso.exclude(ituz__isnull=True).values('ituz').distinct().count(),
        'grids_count': user_qso.exclude(gridsquare__isnull=True).exclude(gridsquare='').values('gridsquare').distinct().count(),
    }

    return render(request, 'dashboard.html', context)


def handle_add_qso(request):
    """
    Обработка добавления QSO вручную
    """
    try:
        # Получаем данные из формы
        my_callsign = request.POST.get('my_callsign', '').strip().upper()
        callsign = request.POST.get('callsign', '').strip().upper()
        date_str = request.POST.get('date', '').strip()
        time_str = request.POST.get('time', '').strip()
        band = request.POST.get('band', '').strip().upper()
        mode = request.POST.get('mode', '').strip().upper()
        rst_rcvd = request.POST.get('rst_rcvd', '').strip().upper()
        rst_sent = request.POST.get('rst_sent', '').strip().upper()
        gridsquare = request.POST.get('his_gridsquare', '').strip().upper()
        my_gridsquare = request.POST.get('my_gridsquare', '').strip().upper()
        state = request.POST.get('state', '').strip().upper()
        sat_qso = 'sat_qso' in request.POST
        prop_mode = request.POST.get('prop_mode', '').strip().upper() if sat_qso else ''
        sat_name = request.POST.get('sat_name', '').strip().upper() if sat_qso else ''

        # Валидация обязательных полей
        if not all([my_callsign, callsign, date_str, time_str, band, mode]):
            messages.error(request, 'Все обязательные поля должны быть заполнены')
            return redirect('dashboard')

        # Валидация форматов
        if len(my_callsign) > 20 or len(callsign) > 20:
            messages.error(request, 'Позывной не должен превышать 20 символов')
            return redirect('dashboard')

        if len(gridsquare) > 8:
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

        # Пересчитываем cqz, ituz, continent, r150s, dxcc, state по позывному
        cqz = None
        ituz = None
        continent = None
        r150s_country = None
        dxcc = None
        state_val = None

        if callsign:
            db_path = os.path.join(settings.BASE_DIR, 'tlog', 'r150cty.dat')
            cty_path = os.path.join(settings.BASE_DIR, 'tlog', 'cty.dat')

            r150s.init_database(db_path)
            r150s.init_cty_database(cty_path)

            dxcc_info = r150s.get_dxcc_info(callsign, db_path)
            if dxcc_info:
                cqz = dxcc_info.get('cq_zone')
                ituz = dxcc_info.get('itu_zone')
                continent = dxcc_info.get('continent')

                r150s_country = dxcc_info.get('country')
                if r150s_country:
                    r150s_country = r150s_country.upper()[:100]

                dxcc = r150s.get_cty_primary_prefix(callsign, cty_path)

            # Определяем код региона России только для российских позывных (UA, UA9, UA2)
            if dxcc and dxcc.upper() in ('UA', 'UA9', 'UA2'):
                exceptions_path = os.path.join(settings.BASE_DIR, 'tlog', 'exceptions.dat')
                region_finder = RussianRegionFinder(exceptions_file=exceptions_path)
                state_val = region_finder.get_region_code(callsign)

        # Создание записи QSO
        try:
            QSO.objects.create(
                user=request.user,
                my_callsign=my_callsign,
                callsign=callsign,
                date=qso_date,
                time=qso_time,
                band=band,
                mode=mode,
                rst_rcvd=rst_rcvd if rst_rcvd else None,
                rst_sent=rst_sent if rst_sent else None,
                gridsquare=gridsquare if gridsquare else None,
                my_gridsquare=my_gridsquare if my_gridsquare else None,
                state=state_val,
                cqz=cqz,
                ituz=ituz,
                continent=continent if continent else None,
                r150s=r150s_country if r150s_country else None,
                dxcc=dxcc if dxcc else None,
                prop_mode=prop_mode if prop_mode else None,
                sat_name=sat_name if sat_name else None,
                lotw='N',
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