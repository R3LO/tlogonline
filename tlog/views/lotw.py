"""
Views для LoTW (Logbook of the World)
"""
import json
import requests
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from ..models import QSO, RadioProfile, check_user_blocked


@login_required
def lotw_page(request):
    """
    Страница LoTW (Logbook of the World) с фильтрацией - доступна только аутентифицированным пользователям
    """
    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    # Получаем данные пользователя для отображения статистики
    context = {}
    
    # Получаем параметры фильтрации (из POST или GET)
    if request.method == 'POST':
        # Проверяем действие (сброс или поиск)
        action = request.POST.get('action', '')
        
        if action == 'reset':
            # Сбрасываем все фильтры
            my_callsign_filter = ''
            search_callsign = ''
            search_qth = ''
            band_filter = ''
            mode_filter = ''
            sat_name_filter = ''
            page = 1
        else:
            # Обычная обработка формы
            my_callsign_filter = request.POST.get('my_callsign', '').strip()
            search_callsign = request.POST.get('search_callsign', '').strip()
            search_qth = request.POST.get('search_qth', '').strip()
            band_filter = request.POST.get('band', '').strip()
            mode_filter = request.POST.get('mode', '').strip()
            sat_name_filter = request.POST.get('sat_name', '').strip()
            page = int(request.POST.get('page', 1))
    else:
        # GET запрос - берем из параметров URL или из кук
        my_callsign_filter = request.GET.get('my_callsign', '').strip() or request.COOKIES.get('lotw_filter_my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip() or request.COOKIES.get('lotw_filter_search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip() or request.COOKIES.get('lotw_filter_search_qth', '').strip()
        band_filter = request.GET.get('band', '').strip() or request.COOKIES.get('lotw_filter_band', '').strip()
        mode_filter = request.GET.get('mode', '').strip() or request.COOKIES.get('lotw_filter_mode', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip() or request.COOKIES.get('lotw_filter_sat_name', '').strip()
        page = int(request.GET.get('page', 1))
        
    # Базовый QuerySet для QSO с LoTW подтверждением
    # Базовый запрос для LoTW подтвержденных QSO
    lotw_qso = QSO.objects.filter(user=request.user, lotw='Y', app_lotw_rxqsl__isnull=False)
    
    # Применяем фильтры
    if my_callsign_filter:
        lotw_qso = lotw_qso.filter(my_callsign__iexact=my_callsign_filter)
    
    if search_callsign:
        lotw_qso = lotw_qso.filter(callsign__icontains=search_callsign)
    
    if search_qth:
        lotw_qso = lotw_qso.filter(gridsquare__icontains=search_qth)
    
    if band_filter:
        lotw_qso = lotw_qso.filter(band=band_filter)
    
    if mode_filter:
        lotw_qso = lotw_qso.filter(mode=mode_filter)
    
    if sat_name_filter:
        lotw_qso = lotw_qso.filter(sat_name=sat_name_filter)
    
    # Получаем уникальные позывные пользователя из базы данных
    try:
        # Получаем уникальные позывные из QSO записей
        my_callsigns_qso = QSO.objects.filter(
            user=request.user
        ).exclude(
            my_callsign__isnull=True
        ).exclude(
            my_callsign__exact=''
        ).values_list('my_callsign', flat=True).distinct().order_by('my_callsign')
        
        # Добавляем username пользователя как дополнительный позывной
        username_callsigns = [request.user.username] if request.user.username else []
        
        # Объединяем и убираем дубликаты
        all_callsigns = list(set(list(my_callsigns_qso) + username_callsigns))
        all_callsigns.sort()
        
        context['my_callsigns'] = all_callsigns
        
        
    except Exception as e:
        context['my_callsigns'] = [request.user.username] if request.user.username else []
    
    # Получаем доступные значения для фильтров (из всех QSO пользователя с LoTW)
    try:
        available_modes = lotw_qso.filter(mode__isnull=False, mode__gt='').values_list('mode', flat=True).distinct().order_by('mode')
        available_bands = lotw_qso.filter(band__isnull=False, band__gt='').values_list('band', flat=True).distinct().order_by('band')
        available_sat_names = lotw_qso.filter(sat_name__isnull=False, sat_name__gt='').values_list('sat_name', flat=True).distinct().order_by('sat_name')
        
        context['available_modes'] = available_modes
        context['available_bands'] = available_bands
        context['available_sat_names'] = available_sat_names
    except Exception as e:
        context['available_modes'] = []
        context['available_bands'] = []
        context['available_sat_names'] = []
    
    # Сохраняем значения фильтров в контекст
    context.update({
        'my_callsign_filter': my_callsign_filter,
        'search_callsign': search_callsign,
        'search_qth': search_qth,
        'band_filter': band_filter,
        'mode_filter': mode_filter,
        'sat_name_filter': sat_name_filter,
    })
    
    # Сортируем по дате LoTW подтверждения (новые сверху)
    lotw_qso_sorted = lotw_qso.order_by('-app_lotw_rxqsl', '-date', '-time')
    
    # Общее количество отфильтрованных записей
    lotw_confirmed_count = lotw_qso_sorted.count()
    context['lotw_confirmed_count'] = lotw_confirmed_count
    
    # Пагинация
    page_size = 20
    if page < 1:
        page = 1
    
    start = (page - 1) * page_size
    end = start + page_size
    total_pages = (lotw_confirmed_count + page_size - 1) // page_size if lotw_confirmed_count > 0 else 1
    
    # Проверяем, что запрашиваемая страница не превышает общее количество страниц
    if page > total_pages:
        page = total_pages
        start = (page - 1) * page_size
        end = start + page_size
    
    # Получаем записи для текущей страницы
    recent_lotw_qso = lotw_qso_sorted[start:end]
    context['recent_lotw_qso'] = recent_lotw_qso
    context['current_page'] = page
    context['total_pages'] = total_pages
    context['page_size'] = page_size
    
    # Статистика для отфильтрованных записей
    try:
        # Всего QSO CFM с учетом фильтров
        total_qso_count = lotw_qso_sorted.count()
        context['total_qso_count'] = total_qso_count
        
        # Уникальные позывные с учетом фильтров
        unique_callsigns_count = lotw_qso_sorted.exclude(callsign__isnull=True).exclude(callsign='').values('callsign').distinct().count()
        context['unique_callsigns_count'] = unique_callsigns_count
        
        # Уникальные DXCC entities
        dxcc_entities = lotw_qso_sorted.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()
        context['dxcc_entities'] = dxcc_entities
        
        # Уникальные R150S entities (страны Р-150-С)
        r150s_entities = lotw_qso_sorted.exclude(r150s__isnull=True).exclude(r150s='').values('r150s').distinct().count()
        context['r150s_entities'] = r150s_entities
        
        # Уникальные регионы России (только для российских DXCC)
        russian_dxcc = ['ASIATIC RUSSIA', 'EUROPEAN RUSSIA', 'KALININGRAD']
        ru_states = lotw_qso_sorted.filter(dxcc__in=russian_dxcc).exclude(state__isnull=True).exclude(state='').values('state').distinct().count()
        context['ru_states'] = ru_states
        
        # Уникальные штаты USA (только для американских DXCC)
        usa_dxcc = ['UNITED STATES OF AMERICA', 'ALASKA', 'HAWAII']
        usa_states = lotw_qso_sorted.filter(dxcc__in=usa_dxcc).exclude(state__isnull=True).exclude(state='').values('state').distinct().count()
        context['usa_states'] = usa_states
        
        # Уникальные провинции Китая (только для китайского DXCC)
        china_states = lotw_qso_sorted.filter(dxcc='CHINA').exclude(state__isnull=True).exclude(state='').values('state').distinct().count()
        context['china_states'] = china_states

        # Уникальные префектуры Японии (только для японского DXCC)
        japan_states = lotw_qso_sorted.filter(dxcc='JAPAN').exclude(state__isnull=True).exclude(state='').values('state').distinct().count()
        context['japan_states'] = japan_states
        
        # Уникальные районы Австралии (только для австралийского DXCC)
        australia_states = lotw_qso_sorted.filter(dxcc='AUSTRALIA').exclude(state__isnull=True).exclude(state='').values('state').distinct().count()
        context['australia_states'] = australia_states

        # Уникальные провинции Канады (только для канадского DXCC)
        canada_states = lotw_qso_sorted.filter(dxcc='CANADA').exclude(state__isnull=True).exclude(state='').values('state').distinct().count()
        context['canada_states'] = canada_states
        
        # Уникальные зоны CQ и ITU (исправленный запрос)
        from django.db.models import IntegerField
        from django.db.models.functions import Coalesce
        
        # CQ зоны
        cq_zones = lotw_qso_sorted.exclude(cqz__isnull=True).values('cqz').distinct().count()
        context['cq_zones'] = cq_zones
        
        # ITU зоны
        itu_zones = lotw_qso_sorted.exclude(ituz__isnull=True).values('ituz').distinct().count()
        context['itu_zones'] = itu_zones
        
        # Уникальные QTH локаторы (оптимизированная версия)
        from django.db.models.functions import Substr
        
        # Получаем уникальные первые 4 символа из gridsquare
        gridsquare_locators = set(
            lotw_qso_sorted.exclude(gridsquare__isnull=True).exclude(gridsquare='').annotate(
                locator_4=Substr('gridsquare', 1, 4)
            ).values_list('locator_4', flat=True).distinct()
        )
        
        # Оптимизированная обработка vucc_grids через генератор
        vucc_qsos = lotw_qso_sorted.exclude(vucc_grids__isnull=True).exclude(vucc_grids='').values_list('vucc_grids', flat=True)
        vucc_locators = set()
        
        # Используем генератор вместо цикла для экономии памяти
        for vucc_grids in vucc_qsos:
            if vucc_grids:
                # Разбиваем и берем первые 4 символа эффективно
                locators = (loc.strip()[:4] for loc in vucc_grids.split(',') if loc.strip() and len(loc.strip()) >= 4)
                vucc_locators.update(locators)
        
        # Объединяем результаты
        all_locators = gridsquare_locators.union(vucc_locators)
        context['qth_locators'] = len(all_locators)
        
        # Уникальные IOTA
        iota_count = lotw_qso_sorted.exclude(iota__isnull=True).exclude(iota='').values('iota').distinct().count()
        context['iota_count'] = iota_count
        
    except Exception as e:
        # Устанавливаем все значения в 0 при ошибке
        context.update({
            'dxcc_entities': 0, 'r150s_entities': 0, 'ru_states': 0, 'usa_states': 0,
            'china_states': 0, 'japan_states': 0, 'australia_states': 0, 'canada_states': 0,
            'cq_zones': 0, 'itu_zones': 0, 'qth_locators': 0, 'iota_count': 0,
            'total_qso_count': 0, 'unique_callsigns_count': 0
        })
    
    # Award credits
    award_credits = lotw_confirmed_count
    context['award_credits'] = award_credits
    
    # Получаем профиль пользователя (оптимизировано с select_related)
    try:
        profile = RadioProfile.objects.select_related('user').get(user=request.user)
        context['profile'] = profile
    except RadioProfile.DoesNotExist:
        # Создаем пустой профиль если его нет
        context['profile'] = RadioProfile(user=request.user)

    return render(request, 'lotw.html', context)


@login_required
def verify_lotw_credentials(request):
    """
    Проверка логина и пароля LoTW
    """
    if request.method != 'POST':
        messages.error(request, 'Метод не поддерживается')
        return redirect('profile_update')

    try:
        # Получаем логин и пароль из POST данных
        login = request.POST.get('lotw_user', '').strip()
        password = request.POST.get('lotw_password', '').strip()

        if not login or not password:
            messages.error(request, 'Логин и пароль обязательны')
            return redirect('profile_update')

        # Функция проверки
        def check_lotw_pass(login, password):
            params = {
                'login': login,
                'password': password,
            }
            response = requests.get(
                "https://lotw.arrl.org/lotwuser/lotwreport.adi",
                params=params,
                timeout=15
            )
            if response.text.strip().startswith('ARRL Logbook of the World Status Report'):
                return True
            elif '<HTML>' in response.text.upper() or '<!DOCTYPE HTML' in response.text.upper():
                return False
            return False

        # Выполняем проверку
        is_valid = check_lotw_pass(login, password)

        # Обновляем профиль пользователя
        try:
            profile = RadioProfile.objects.get(user=request.user)
            profile.lotw_chk_pass = is_valid
            if is_valid:
                profile.lotw_user = login
                profile.lotw_password = password
            profile.save()
            
            if is_valid:
                messages.success(request, 'Логин и пароль проверены и сохранены успешно')
            else:
                messages.error(request, 'Логин или пароль неверны. Проверьте данные и попробуйте снова.')
        except RadioProfile.DoesNotExist:
            messages.error(request, 'Профиль пользователя не найден')
            
        return redirect('profile_update')

    except Exception as e:
        messages.error(request, f'Ошибка при проверке: {str(e)}')
        return redirect('profile_update')


@login_required
def debug_user_qso(request):
    """
    Отладочная функция для проверки QSO записей пользователя
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        user = request.user
        user_id = user.id
        username = user.username
        
        # Получаем все QSO записи пользователя
        all_qsos = QSO.objects.filter(user=user_id)
        
        # Получаем записи с my_callsign
        qsos_with_callsign = all_qsos.exclude(
            my_callsign__isnull=True
        ).exclude(
            my_callsign__=''
        ).exclude(
            my_callsign__exact=None
        )
        
        # Получаем уникальные позывные
        unique_callsigns = list(qsos_with_callsign.values_list('my_callsign', flat=True).distinct())
        
        # Статистика
        stats = {
            'user_info': {
                'id': user_id,
                'username': username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'qso_stats': {
                'total_qso_count': all_qsos.count(),
                'qso_with_my_callsign_count': qsos_with_callsign.count(),
                'unique_my_callsigns_count': len(unique_callsigns),
            },
            'sample_qsos': [],
            'unique_my_callsigns': unique_callsigns,
        }
        
        # Добавляем примеры записей (первые 5)
        sample_qsos = all_qsos[:5]
        for qso in sample_qsos:
            stats['sample_qsos'].append({
                'id': str(qso.id),
                'my_callsign': qso.my_callsign,
                'callsign': qso.callsign,
                'band': qso.band,
                'mode': qso.mode,
                'date': qso.date.strftime('%Y-%m-%d') if qso.date else None,
                'time': qso.time.strftime('%H:%M') if qso.time else None,
                'created_at': qso.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({
            'success': True,
            'debug_data': stats
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def lotw_japan_prefectures_api(request):
    """
    API endpoint для получения данных префектур Японии с учетом фильтров LoTW
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        from collections import defaultdict

        # Получаем параметры фильтрации
        my_callsign_filter = request.GET.get('my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip()
        band_filter = request.GET.get('band', '').strip()
        mode_filter = request.GET.get('mode', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip()

        # Базовый QuerySet для QSO с LoTW подтверждением
        lotw_qso = QSO.objects.filter(
            user=request.user,
            lotw='Y',
            app_lotw_rxqsl__isnull=False
        )

        # Применяем фильтры
        if my_callsign_filter:
            lotw_qso = lotw_qso.filter(my_callsign__iexact=my_callsign_filter)

        if search_callsign:
            lotw_qso = lotw_qso.filter(callsign__icontains=search_callsign)

        if search_qth:
            lotw_qso = lotw_qso.filter(gridsquare__icontains=search_qth)

        if band_filter:
            lotw_qso = lotw_qso.filter(band=band_filter)

        if mode_filter:
            lotw_qso = lotw_qso.filter(mode=mode_filter)

        if sat_name_filter:
            lotw_qso = lotw_qso.filter(sat_name=sat_name_filter)

        # Фильтруем только японский DXCC
        lotw_qso = lotw_qso.filter(dxcc='JAPAN')

        # Получаем уникальные пары my_callsign + префектура + callsign
        qso_filtered = lotw_qso.filter(
            state__isnull=False
        ).exclude(state='').values('my_callsign', 'state', 'callsign').distinct()

        # Группируем по my_callsign, затем по префектуре
        callsign_data = defaultdict(lambda: defaultdict(set))

        for item in qso_filtered:
            my_call = item['my_callsign']
            prefecture_code = item['state']
            call = item['callsign']
            callsign_data[my_call][prefecture_code].add(call)

        # Формируем список с позывным, количеством и данными префектур
        ratings = []
        for my_call, prefectures_dict in callsign_data.items():
            prefectures_list = []
            for prefecture_code, callsigns in prefectures_dict.items():
                prefectures_list.append({
                    'code': prefecture_code,
                    'callsigns': sorted(list(callsigns))
                })
            # Сортируем по коду префектуры
            prefectures_list.sort(key=lambda x: x['code'])

            ratings.append({
                'callsign': my_call,
                'count': len(prefectures_list),
                'prefectures': prefectures_list
            })

        # Сортируем по количеству (убывание), затем по позывному
        ratings.sort(key=lambda x: (-x['count'], x['callsign']))

        # Подсчитываем общее количество префектур
        total_prefectures = sum(item['count'] for item in ratings)

        return JsonResponse({
            'success': True,
            'ratings': ratings,
            'total_prefectures': total_prefectures,
            'filters': {
                'my_callsign': my_callsign_filter,
                'search_callsign': search_callsign,
                'search_qth': search_qth,
                'band': band_filter,
                'mode': mode_filter,
                'sat_name': sat_name_filter,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def lotw_china_provinces_api(request):
    """
    API endpoint для получения данных провинций Китая с учетом фильтров LoTW
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        from collections import defaultdict

        # Получаем параметры фильтрации
        my_callsign_filter = request.GET.get('my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip()
        band_filter = request.GET.get('band', '').strip()
        mode_filter = request.GET.get('mode', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip()

        # Базовый QuerySet для QSO с LoTW подтверждением
        lotw_qso = QSO.objects.filter(
            user=request.user,
            lotw='Y',
            app_lotw_rxqsl__isnull=False
        )

        # Применяем фильтры
        if my_callsign_filter:
            lotw_qso = lotw_qso.filter(my_callsign__iexact=my_callsign_filter)

        if search_callsign:
            lotw_qso = lotw_qso.filter(callsign__icontains=search_callsign)

        if search_qth:
            lotw_qso = lotw_qso.filter(gridsquare__icontains=search_qth)

        if band_filter:
            lotw_qso = lotw_qso.filter(band=band_filter)

        if mode_filter:
            lotw_qso = lotw_qso.filter(mode=mode_filter)

        if sat_name_filter:
            lotw_qso = lotw_qso.filter(sat_name=sat_name_filter)

        # Фильтруем только китайский DXCC
        lotw_qso = lotw_qso.filter(dxcc='CHINA')

        # Получаем уникальные пары my_callsign + провинция + callsign
        qso_filtered = lotw_qso.filter(
            state__isnull=False
        ).exclude(state='').values('my_callsign', 'state', 'callsign').distinct()

        # Группируем по my_callsign, затем по провинции
        callsign_data = defaultdict(lambda: defaultdict(set))

        for item in qso_filtered:
            my_call = item['my_callsign']
            province_code = item['state']
            call = item['callsign']
            callsign_data[my_call][province_code].add(call)

        # Формируем список с позывным, количеством и данными провинций
        ratings = []
        for my_call, provinces_dict in callsign_data.items():
            provinces_list = []
            for province_code, callsigns in provinces_dict.items():
                provinces_list.append({
                    'code': province_code,
                    'callsigns': sorted(list(callsigns))
                })
            # Сортируем по коду провинции
            provinces_list.sort(key=lambda x: x['code'])

            ratings.append({
                'callsign': my_call,
                'count': len(provinces_list),
                'provinces': provinces_list
            })

        # Сортируем по количеству (убывание), затем по позывному
        ratings.sort(key=lambda x: (-x['count'], x['callsign']))

        # Подсчитываем общее количество провинций
        total_provinces = sum(item['count'] for item in ratings)

        return JsonResponse({
            'success': True,
            'ratings': ratings,
            'total_provinces': total_provinces,
            'filters': {
                'my_callsign': my_callsign_filter,
                'search_callsign': search_callsign,
                'search_qth': search_qth,
                'band': band_filter,
                'mode': mode_filter,
                'sat_name': sat_name_filter,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def lotw_usa_states_api(request):
    """
    API endpoint для получения данных штатов USA с учетом фильтров LoTW
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        from collections import defaultdict

        # Получаем параметры фильтрации
        my_callsign_filter = request.GET.get('my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip()
        band_filter = request.GET.get('band', '').strip()
        mode_filter = request.GET.get('mode', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip()

        # Базовый QuerySet для QSO с LoTW подтверждением
        lotw_qso = QSO.objects.filter(
            user=request.user,
            lotw='Y',
            app_lotw_rxqsl__isnull=False
        )

        # Применяем фильтры
        if my_callsign_filter:
            lotw_qso = lotw_qso.filter(my_callsign__iexact=my_callsign_filter)

        if search_callsign:
            lotw_qso = lotw_qso.filter(callsign__icontains=search_callsign)

        if search_qth:
            lotw_qso = lotw_qso.filter(gridsquare__icontains=search_qth)

        if band_filter:
            lotw_qso = lotw_qso.filter(band=band_filter)

        if mode_filter:
            lotw_qso = lotw_qso.filter(mode=mode_filter)

        if sat_name_filter:
            lotw_qso = lotw_qso.filter(sat_name=sat_name_filter)

        # Фильтруем только американские DXCC
        usa_dxcc = ['UNITED STATES OF AMERICA', 'ALASKA', 'HAWAII']
        lotw_qso = lotw_qso.filter(dxcc__in=usa_dxcc)

        # Получаем уникальные пары my_callsign + штат + callsign
        qso_filtered = lotw_qso.filter(
            state__isnull=False
        ).exclude(state='').values('my_callsign', 'state', 'callsign').distinct()

        # Группируем по my_callsign, затем по штату
        callsign_data = defaultdict(lambda: defaultdict(set))

        for item in qso_filtered:
            my_call = item['my_callsign']
            state_code = item['state']
            call = item['callsign']
            callsign_data[my_call][state_code].add(call)

        # Формируем список с позывным, количеством и данными штатов
        ratings = []
        for my_call, states_dict in callsign_data.items():
            states_list = []
            for state_code, callsigns in states_dict.items():
                states_list.append({
                    'code': state_code,
                    'callsigns': sorted(list(callsigns))
                })
            # Сортируем по коду штата
            states_list.sort(key=lambda x: x['code'])

            ratings.append({
                'callsign': my_call,
                'count': len(states_list),
                'states': states_list
            })

        # Сортируем по количеству (убывание), затем по позывному
        ratings.sort(key=lambda x: (-x['count'], x['callsign']))

        # Подсчитываем общее количество штатов
        total_states = sum(item['count'] for item in ratings)

        return JsonResponse({
            'success': True,
            'ratings': ratings,
            'total_states': total_states,
            'filters': {
                'my_callsign': my_callsign_filter,
                'search_callsign': search_callsign,
                'search_qth': search_qth,
                'band': band_filter,
                'mode': mode_filter,
                'sat_name': sat_name_filter,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_user_callsigns(request):
    """
    API endpoint для получения списка позывных пользователя
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        user = request.user
        user_id = user.id
        username = user.username
        
        # Получаем уникальные позывные пользователя (оптимизировано)
        # Используем только нужные поля и индексы
        qsos_for_user = QSO.objects.filter(user=user_id).only('my_callsign')
        
        # Фильтруем записи с непустыми my_callsign (используем быстрые запросы)
        my_callsigns_query = qsos_for_user.exclude(
            my_callsign__isnull=True
        ).exclude(
            my_callsign__exact=''
        )
        
        # Получаем уникальные позывные (оптимизировано)
        my_callsigns = list(my_callsigns_query.values_list('my_callsign', flat=True).distinct())
        my_callsigns.sort()
        
        # Добавляем username пользователя как дополнительный позывной
        username_callsigns = [username] if username else []
        
        # Объединяем и убираем дубликаты
        all_callsigns = list(set(my_callsigns + username_callsigns))
        all_callsigns.sort()
        
        return JsonResponse({
            'success': True,
            'callsigns': all_callsigns,
            'debug_info': {
                'user_id': user_id,
                'username': username,
                'total_qso_count': qsos_for_user.count(),
                'qso_with_callsign_count': my_callsigns_query.count(),
                'unique_callsigns_count': len(my_callsigns)
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def lotw_filter_api(request):
    """
    API endpoint для AJAX фильтрации LoTW записей
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        # Получаем параметры фильтрации из JSON
        data = json.loads(request.body)
        my_callsign_filter = data.get('my_callsign', '').strip()
        search_callsign = data.get('search_callsign', '').strip()
        search_qth = data.get('search_qth', '').strip()
        band_filter = data.get('band', '').strip()
        mode_filter = data.get('mode', '').strip()
        sat_name_filter = data.get('sat_name', '').strip()
        page = int(data.get('page', 1))

        # Базовый QuerySet для QSO с LoTW подтверждением (оптимизировано)
        # Используем только нужные поля для минимизации передачи данных
        lotw_qso = QSO.objects.filter(
            user=request.user, 
            lotw='Y', 
            app_lotw_rxqsl__isnull=False
        ).only(
            'id', 'date', 'time', 'my_callsign', 'callsign', 'band', 'frequency', 
            'mode', 'gridsquare', 'r150s', 'state', 'prop_mode', 'sat_name', 'app_lotw_rxqsl'
        )
        
        # Применяем фильтры
        if my_callsign_filter:
            lotw_qso = lotw_qso.filter(my_callsign__iexact=my_callsign_filter)
        
        if search_callsign:
            lotw_qso = lotw_qso.filter(callsign__icontains=search_callsign)
        
        if search_qth:
            lotw_qso = lotw_qso.filter(gridsquare__icontains=search_qth)
        
        if band_filter:
            lotw_qso = lotw_qso.filter(band=band_filter)
        
        if mode_filter:
            lotw_qso = lotw_qso.filter(mode=mode_filter)
        
        if sat_name_filter:
            lotw_qso = lotw_qso.filter(sat_name=sat_name_filter)
        
        # Сортируем по дате LoTW подтверждения (новые сверху)
        lotw_qso_sorted = lotw_qso.order_by('-app_lotw_rxqsl', '-date', '-time')
        
        # Общее количество отфильтрованных записей
        lotw_confirmed_count = lotw_qso_sorted.count()
        
        # Пагинация
        page_size = 20
        if page < 1:
            page = 1
        
        start = (page - 1) * page_size
        end = start + page_size
        total_pages = (lotw_confirmed_count + page_size - 1) // page_size if lotw_confirmed_count > 0 else 1
        
        # Проверяем, что запрашиваемая страница не превышает общее количество страниц
        if page > total_pages:
            page = total_pages
            start = (page - 1) * page_size
            end = start + page_size
        
        # Получаем записи для текущей страницы
        recent_lotw_qso = lotw_qso_sorted[start:end]
        
        # Подготавливаем данные для JSON ответа
        qso_data = []
        for qso in recent_lotw_qso:
            qso_data.append({
                'id': str(qso.id),
                'date': qso.date.strftime('%d.%m.%Y'),
                'time': qso.time.strftime('%H:%M') if qso.time else '',
                'my_callsign': qso.my_callsign or qso.user.username,
                'callsign': qso.callsign,
                'band': qso.band or '',
                'frequency': str(qso.frequency) if qso.frequency else '',
                'mode': qso.mode or '',
                'gridsquare': qso.gridsquare or '',
                'r150s': qso.r150s or '',
                'state': qso.state or '',
                'prop_mode': qso.prop_mode or '',
                'sat_name': qso.sat_name or '',
                'lotw_date': qso.app_lotw_rxqsl.strftime('%d.%m.%Y') if qso.app_lotw_rxqsl else '',
            })
        
        # DXCC entities для отфильтрованных записей
        try:
            dxcc_entities = lotw_qso_sorted.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()
        except Exception as e:
            dxcc_entities = 0

        return JsonResponse({
            'success': True,
            'qso_data': qso_data,
            'total_count': lotw_confirmed_count,
            'current_page': page,
            'total_pages': total_pages,
            'award_credits': lotw_confirmed_count,
            'filters': {
                'my_callsign': my_callsign_filter,
                'search_callsign': search_callsign,
                'search_qth': search_qth,
                'band': band_filter,
                'mode': mode_filter,
                'sat_name': sat_name_filter,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_qso_details(request):
    """
    API endpoint для получения полных данных QSO по ID
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        qso_id = request.GET.get('qso_id')
        if not qso_id:
            return JsonResponse({'error': 'ID QSO не указан'}, status=400)

        # Получаем QSO запись (оптимизировано - только нужные поля)
        try:
            qso = QSO.objects.only(
                'id', 'date', 'time', 'my_callsign', 'callsign', 'frequency', 'band', 'mode',
                'rst_sent', 'rst_rcvd', 'my_gridsquare', 'gridsquare', 'continent', 'state',
                'prop_mode', 'sat_name', 'r150s', 'dxcc', 'cqz', 'ituz', 'vucc_grids', 
                'iota', 'lotw', 'paper_qsl', 'app_lotw_rxqsl', 'created_at', 'updated_at'
            ).get(id=qso_id, user=request.user)
        except QSO.DoesNotExist:
            return JsonResponse({'error': 'QSO не найдено'}, status=404)

        # Подготавливаем все данные QSO
        qso_data = {
            'id': str(qso.id),
            'date': qso.date.strftime('%Y-%m-%d') if qso.date else '',
            'time': qso.time.strftime('%H:%M:%S') if qso.time else '',
            'my_callsign': qso.my_callsign or '',
            'callsign': qso.callsign or '',
            'frequency': str(qso.frequency) if qso.frequency else '',
            'band': qso.band or '',
            'mode': qso.mode or '',
            'rst_sent': qso.rst_sent or '',
            'rst_rcvd': qso.rst_rcvd or '',
            'my_gridsquare': qso.my_gridsquare or '',
            'gridsquare': qso.gridsquare or '',
            'continent': qso.continent or '',
            'state': qso.state or '',
            'prop_mode': qso.prop_mode or '',
            'sat_name': qso.sat_name or '',
            'r150s': qso.r150s or '',
            'dxcc': qso.dxcc or '',
            'cqz': qso.cqz if qso.cqz is not None else '',
            'ituz': qso.ituz if qso.ituz is not None else '',
            'vucc_grids': qso.vucc_grids or '',
            'iota': qso.iota or '',
            'lotw': qso.lotw or '',
            'paper_qsl': qso.paper_qsl or '',
            'app_lotw_rxqsl': qso.app_lotw_rxqsl.strftime('%Y-%m-%d %H:%M:%S') if qso.app_lotw_rxqsl else '',
            'created_at': qso.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': qso.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return JsonResponse({
            'success': True,
            'qso_data': qso_data
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def export_lotw_adif(request):
    """
    Экспорт только LoTW подтвержденных QSO в ADIF файл с учетом фильтров
    """
    try:
        # Получаем параметры фильтрации (те же что в lotw view)
        my_callsign_filter = request.GET.get('my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip()
        band_filter = request.GET.get('band', '').strip()
        mode_filter = request.GET.get('mode', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip()

        # Базовый QuerySet для QSO с LoTW подтверждением
        lotw_qso = QSO.objects.filter(user=request.user, lotw='Y', app_lotw_rxqsl__isnull=False)

        # Применяем фильтры
        if my_callsign_filter:
            lotw_qso = lotw_qso.filter(my_callsign__iexact=my_callsign_filter)
        
        if search_callsign:
            lotw_qso = lotw_qso.filter(callsign__icontains=search_callsign)
        
        if search_qth:
            lotw_qso = lotw_qso.filter(gridsquare__icontains=search_qth)
        
        if band_filter:
            lotw_qso = lotw_qso.filter(band=band_filter)
        
        if mode_filter:
            lotw_qso = lotw_qso.filter(mode=mode_filter)
        
        if sat_name_filter:
            lotw_qso = lotw_qso.filter(sat_name=sat_name_filter)
        
        # Сортируем по дате LoTW подтверждения
        lotw_qso = lotw_qso.order_by('-app_lotw_rxqsl', '-date', '-time')

        # Формируем ADIF файл (используем существующую функцию из logbook)
        adif_content = generate_lotw_adif_content(lotw_qso)

        # Получаем позывной пользователя для имени файла
        try:
            user_callsign = request.user.radio_profile.callsign or request.user.username
        except:
            user_callsign = request.user.username

        # Формируем имя файла с указанием LoTW
        filename = f"{user_callsign}_LoTW.adi"

        response = HttpResponse(adif_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        messages.error(request, f'Ошибка при формировании ADIF файла: {str(e)}')
        return redirect('lotw_page')


def generate_lotw_adif_content(qso_queryset):
    """
    Генерирует содержимое ADIF файла для LoTW записей с дополнительными полями LoTW
    """
    lines = []

    # Заголовок ADIF для LoTW
    lines.append('ADIF Export from TLog - LoTW Records Only')
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

        if qso.dxcc:
            record_parts.append(f'<DXCC:{len(qso.dxcc)}>{qso.dxcc}')

        if qso.state:
            record_parts.append(f'<STATE:{len(qso.state)}>{qso.state}')

        if qso.iota:
            record_parts.append(f'<IOTA:{len(qso.iota)}>{qso.iota}')

        if qso.vucc_grids:
            record_parts.append(f'<VUCC_GRIDS:{len(qso.vucc_grids)}>{qso.vucc_grids}')

        # LoTW специфичные поля
        if qso.lotw == 'Y':
            record_parts.append(f'<LOTW_RXQSL:1>Y')
            
        if qso.app_lotw_rxqsl:
            lotw_date_str = qso.app_lotw_rxqsl.strftime('%Y%m%d')
            record_parts.append(f'<LOTW_QSLRDATE:8>{lotw_date_str}')

        # Добавляем запись
        if record_parts:
            lines.append(' '.join(record_parts) + ' <EOR>')

    return '\n'.join(lines)


@login_required
def delete_lotw_credentials(request):
    """
    Удаление логина и пароля LoTW
    """
    if request.method != 'POST':
        messages.error(request, 'Метод не поддерживается')
        return redirect('profile_update')

    try:
        profile = RadioProfile.objects.get(user=request.user)
        profile.lotw_user = ''
        profile.lotw_password = ''
        profile.lotw_chk_pass = False
        profile.save()

        messages.success(request, 'Логин и пароль LoTW удалены успешно')
        return redirect('profile_update')

    except RadioProfile.DoesNotExist:
        messages.error(request, 'Профиль пользователя не найден')
        return redirect('profile_update')
    except Exception as e:
        messages.error(request, f'Ошибка при удалении: {str(e)}')
        return redirect('profile_update')


@login_required
def lotw_regions_api(request):
    """
    API endpoint для получения данных регионов России с учетом фильтров LoTW
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        from tlog.region_ru import RussianRegionFinder
        from collections import defaultdict

        # Получаем параметры фильтрации
        my_callsign_filter = request.GET.get('my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip()
        band_filter = request.GET.get('band', '').strip()
        mode_filter = request.GET.get('mode', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip()

        # Базовый QuerySet для QSO с LoTW подтверждением
        lotw_qso = QSO.objects.filter(
            user=request.user,
            lotw='Y',
            app_lotw_rxqsl__isnull=False
        )

        # Применяем фильтры
        if my_callsign_filter:
            lotw_qso = lotw_qso.filter(my_callsign__iexact=my_callsign_filter)

        if search_callsign:
            lotw_qso = lotw_qso.filter(callsign__icontains=search_callsign)

        if search_qth:
            lotw_qso = lotw_qso.filter(gridsquare__icontains=search_qth)

        if band_filter:
            lotw_qso = lotw_qso.filter(band=band_filter)

        if mode_filter:
            lotw_qso = lotw_qso.filter(mode=mode_filter)

        if sat_name_filter:
            lotw_qso = lotw_qso.filter(sat_name=sat_name_filter)

        # Фильтруем только российские DXCC
        russian_dxcc = ['ASIATIC RUSSIA', 'EUROPEAN RUSSIA', 'KALININGRAD']
        lotw_qso = lotw_qso.filter(dxcc__in=russian_dxcc)

        # Получаем уникальные пары my_callsign + регион + callsign
        qso_filtered = lotw_qso.filter(
            state__isnull=False
        ).exclude(state='').values('my_callsign', 'state', 'callsign').distinct()

        # Группируем по my_callsign, затем по региону
        callsign_data = defaultdict(lambda: defaultdict(set))

        for item in qso_filtered:
            my_call = item['my_callsign']
            region_code = item['state']
            call = item['callsign']
            callsign_data[my_call][region_code].add(call)

        # Получаем данные регионов
        region_finder = RussianRegionFinder()

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

        # Подсчитываем общее количество регионов
        total_regions = sum(item['count'] for item in ratings)

        return JsonResponse({
            'success': True,
            'ratings': ratings,
            'total_regions': total_regions,
            'filters': {
                'my_callsign': my_callsign_filter,
                'search_callsign': search_callsign,
                'search_qth': search_qth,
                'band': band_filter,
                'mode': mode_filter,
                'sat_name': sat_name_filter,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
