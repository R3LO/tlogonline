"""
Views для LoTW (Logbook of the World)
"""
import json
import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
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
        my_callsign_filter = request.GET.get('my_callsign', '').strip()
        search_callsign = request.GET.get('search_callsign', '').strip()
        search_qth = request.GET.get('search_qth', '').strip()
        band_filter = request.GET.get('band', '').strip()
        mode_filter = request.GET.get('mode', '').strip()
        sat_name_filter = request.GET.get('sat_name', '').strip()
        page = int(request.GET.get('page', 1))
        
    # Общая статистика QSO
    total_qso_count = QSO.objects.filter(user=request.user).count()
    context['total_qso_count'] = total_qso_count
    
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
        
        print(f"📞 Загружено позывных для {request.user.username}: {len(all_callsigns)}")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки позывных: {e}")
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
    
    # Уникальные DXCC entities для отфильтрованных записей
    try:
        dxcc_entities = lotw_qso_sorted.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()
        context['dxcc_entities'] = dxcc_entities
    except Exception as e:
        context['dxcc_entities'] = 0
    
    # Award credits
    award_credits = lotw_confirmed_count
    context['award_credits'] = award_credits
    
    # Получаем профиль пользователя
    try:
        profile = RadioProfile.objects.get(user=request.user)
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
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        # Получаем логин и пароль из POST данных
        data = json.loads(request.body)
        login = data.get('login', '').strip()
        password = data.get('password', '').strip()

        if not login or not password:
            return JsonResponse({'error': 'Логин и пароль обязательны'}, status=400)

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
        except RadioProfile.DoesNotExist:
            pass

        return JsonResponse({
            'success': True,
            'is_valid': is_valid,
            'message': 'Логин и пароль верны' if is_valid else 'Логин или пароль неверны'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
        
        # Получаем уникальные позывные пользователя из базы данных QSO
        qsos_for_user = QSO.objects.filter(user=user_id)
        
        # Фильтруем записи с непустыми my_callsign
        my_callsigns_query = qsos_for_user.exclude(
            my_callsign__isnull=True
        ).exclude(
            my_callsign__exact=''
        )
        
        print(f"📝 Записей с my_callsign: {my_callsigns_query.count()}")
        
        # Получаем уникальные позывные
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
                'ru_region': qso.ru_region or '',
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
            'dxcc_entities': dxcc_entities,
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

        # Получаем QSO запись
        try:
            qso = QSO.objects.get(id=qso_id, user=request.user)
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
            'ru_region': qso.ru_region or '',
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
def delete_lotw_credentials(request):
    """
    Удаление логина и пароля LoTW
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        profile = RadioProfile.objects.get(user=request.user)
        profile.lotw_user = ''
        profile.lotw_password = ''
        profile.lotw_chk_pass = False
        profile.save()

        return JsonResponse({'success': True})

    except RadioProfile.DoesNotExist:
        return JsonResponse({'error': 'Профиль не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
