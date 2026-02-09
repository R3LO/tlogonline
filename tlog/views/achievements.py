"""
Представления для достижений
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..models import QSO, check_user_blocked
def achievements(request):
    """
    Мои достижения - статистика и награды (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)
    """
    import json
    from django.db.models import Count
    from ..models import QSO, ADIFUpload
    from django.utils import timezone
    from django.template.loader import render_to_string
    from django.core.cache import cache
    from django.contrib.auth.decorators import login_required
    from datetime import timedelta

    # Проверяем аутентификацию пользователя
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Проверяем, не заблокирован ли пользователь
    is_blocked, reason = check_user_blocked(request.user)
    if is_blocked:
        return render(request, 'blocked.html', {'reason': reason})

    user = request.user

    # Обработка POST запроса с фильтрами
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            my_callsign_filter = data.get('my_callsign', '').strip()
            band_filter = data.get('band', '').strip()
            mode_filter = data.get('mode', '').strip()
            prop_mode_filter = data.get('prop_mode', '').strip()
            sat_name_filter = data.get('sat_name', '').strip()

            # Базовый QuerySet
            qso_queryset = QSO.objects.filter(user=user)

            # Применяем фильтры
            if my_callsign_filter:
                qso_queryset = qso_queryset.filter(my_callsign__iexact=my_callsign_filter)
            if band_filter:
                qso_queryset = qso_queryset.filter(band=band_filter)
            if mode_filter:
                qso_queryset = qso_queryset.filter(mode=mode_filter)
            if prop_mode_filter:
                qso_queryset = qso_queryset.filter(prop_mode=prop_mode_filter)
            if sat_name_filter:
                qso_queryset = qso_queryset.filter(sat_name=sat_name_filter)

            # Оптимизированная статистика с фильтрами (все в одном запросе)
            total_qso = qso_queryset.count()

            # Статистика по диапазонам (один запрос)
            band_counts = dict(qso_queryset.filter(band__isnull=False, band__gt='')
                               .values('band').annotate(count=Count('id')).values_list('band', 'count'))
            
            # Статистика по модуляциям (один запрос)
            mode_counts = dict(qso_queryset.filter(mode__isnull=False, mode__gt='')
                               .values('mode').annotate(count=Count('id')).values_list('mode', 'count'))

            # Уникальные значения (оптимизированные запросы)
            unique_callsigns = user_qsos.filter(callsign__isnull=False, callsign__gt='').values('callsign').distinct().count()
            r150s_count = user_qsos.filter(r150s__isnull=False, r150s__gt='').values('r150s').distinct().count()
            dxcc_count = user_qsos.filter(dxcc__isnull=False, dxcc__gt='').values('dxcc').distinct().count()
            state_count = user_qsos.filter(state__isnull=False, state__gt='').values('state').distinct().count()
            cqz_count = user_qsos.filter(cqz__isnull=False).values('cqz').distinct().count()
            ituz_count = user_qsos.filter(ituz__isnull=False).values('ituz').distinct().count()
            grids_count = user_qsos.filter(gridsquare__isnull=False, gridsquare__gt='').values('gridsquare').distinct().count()
            
            # Уникальные мои позывные
            my_callsigns = list(user_qsos.filter(my_callsign__isnull=False, my_callsign__gt='')
                               .values_list('my_callsign', flat=True).distinct().order_by('my_callsign'))

            # Достижения (awards)
            achievements = []

            # 100 QSO
            if total_qso >= 100:
                achievements.append({
                    'title': 'Новичок',
                    'description': 'Зарегистрировано 100+ QSO',
                    'icon': '🎯',
                    'unlocked': True
                })

            # 500 QSO
            if total_qso >= 500:
                achievements.append({
                    'title': 'Опытный',
                    'description': 'Зарегистрировано 500+ QSO',
                    'icon': '⭐',
                    'unlocked': True
                })

            # 1000 QSO
            if total_qso >= 1000:
                achievements.append({
                    'title': 'Мастер',
                    'description': 'Зарегистрировано 1000+ QSO',
                    'icon': '🏆',
                    'unlocked': True
                })

            # 10 диапазонов
            if len(band_counts) >= 10:
                achievements.append({
                    'title': 'Разведчик',
                    'description': 'Связи на 10+ диапазонах',
                    'icon': '📡',
                    'unlocked': True
                })

            # 5 видов модуляций
            if len(mode_counts) >= 5:
                achievements.append({
                    'title': 'Универсал',
                    'description': 'Связи на 5+ видах модуляции',
                    'icon': '🎛️',
                    'unlocked': True
                })

            # 50 стран Р-150-С
            if r150s_count >= 50:
                achievements.append({
                    'title': 'Охотник за DX',
                    'description': 'Связи с 50+ странами Р-150-С',
                    'icon': '🌍',
                    'unlocked': True
                })

            # 100 стран Р-150-С
            if r150s_count >= 100:
                achievements.append({
                    'title': 'Патриот',
                    'description': 'Связи со 100+ странами Р-150-С',
                    'icon': '🎖️',
                    'unlocked': True
                })

            # LoTW подтверждения
            if lotw_count >= 10:
                achievements.append({
                    'title': 'Цифровой оператор',
                    'description': '10+ подтверждений LoTW',
                    'icon': '💻',
                    'unlocked': True
                })

            # Активность за неделю
            if week_qso >= 50:
                achievements.append({
                    'title': 'В эфире',
                    'description': '50+ связей за неделю',
                    'icon': '📻',
                    'unlocked': True
                })

            # === Награды QO-100 (оптимизировано) ===
            # QO-100 статистика с LoTW (оптимизированный запрос)
            qo100_lotw_stats = user_qsos.filter(sat_name='QO-100', lotw='Y').aggregate(
                states=Count('state', filter=Q(state__isnull=False, state__gt='')),
                countries=Count('r150s', filter=Q(r150s__isnull=False, r150s__gt='')),
                grids=Count('gridsquare', filter=Q(gridsquare__isnull=False, gridsquare__gt='')),
                callsigns=Count('callsign', filter=Q(callsign__isnull=False, callsign__gt=''))
            )

            # QO-100 общая статистика
            qo100_all_callsigns = user_qsos.filter(sat_name='QO-100').values('callsign').distinct().count()

            # Награды QO-100
            if qo100_lotw_stats['states'] >= 25:
                achievements.append({
                    'title': 'W-QO100-R',
                    'description': '25+ регионов РФ через QO-100 (LoTW)',
                    'icon': '🗺️',
                    'unlocked': True
                })

            if qo100_lotw_stats['states'] >= 30:
                achievements.append({
                    'title': 'W-QO100-PROFI',
                    'description': '30+ регионов РФ через QO-100 (LoTW)',
                    'icon': '🎓',
                    'unlocked': True
                })

            if qo100_lotw_stats['countries'] >= 100:
                achievements.append({
                    'title': 'W-QO100-C',
                    'description': '100+ стран через QO-100 (LoTW)',
                    'icon': '🌐',
                    'unlocked': True
                })

            if qo100_lotw_stats['grids'] >= 500:
                achievements.append({
                    'title': 'W-QO100-L',
                    'description': '500+ QTH локаторов через QO-100 (LoTW)',
                    'icon': '📍',
                    'unlocked': True
                })

            if qo100_lotw_stats['callsigns'] >= 1000:
                achievements.append({
                    'title': 'W-QO100-U',
                    'description': '1000+ позывных через QO-100 (LoTW)',
                    'icon': '📡',
                    'unlocked': True
                })

            if qo100_all_callsigns >= 1000:
                achievements.append({
                    'title': 'W-QO100-B',
                    'description': '1000+ связей через QO-100',
                    'icon': '🛰️',
                    'unlocked': True
                })

            # Формируем HTML достижений
            achievements_html = ''
            for achievement in achievements:
                achievements_html += f'''
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="achievement-card unlocked">
                        <div class="achievement-icon">{achievement['icon']}</div>
                        <div class="achievement-title">{achievement['title']}</div>
                        <div class="achievement-description">{achievement['description']}</div>
                    </div>
                </div>
                '''

            # Формируем сообщение о применённых фильтрах
            filter_parts = []
            if band_filter:
                filter_parts.append(f'диапазон {band_filter}')
            if mode_filter:
                filter_parts.append(f'вид связи {mode_filter}')
            if prop_mode_filter:
                filter_parts.append(f'prop_mode {prop_mode_filter}')
            if sat_name_filter:
                filter_parts.append(f'спутник {sat_name_filter}')

            if filter_parts:
                message = f'Отфильтровано по: {", ".join(filter_parts)}. Найдено {total_qso} QSO'
            else:
                message = f'Найдено {total_qso} QSO'

            return JsonResponse({
                'success': True,
                'total_qso': total_qso,
                'bands': band_counts,
                'modes': mode_counts,
                'unique_callsigns': unique_callsigns,
                'dxcc_count': dxcc_count,
                'r150s_count': r150s_count,
                'state_count': state_count,
                'cqz_count': cqz_count,
                'ituz_count': ituz_count,
                'grids_count': grids_count,
                'achievements': achievements,
                'achievements_html': achievements_html,
                'message': message
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Неверный формат данных'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # GET запрос - обычная загрузка страницы (ОПТИМИЗИРОВАННАЯ)
    
    # Проверяем кэш для пользователя (кэшируем на 5 минут)
    cache_key = f'achievements_{user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return render(request, 'achievements_base.html', cached_data)

    # Базовая статистика пользователя
    user_qsos = QSO.objects.filter(user=user)
    
    # Проверяем, есть ли данные для пользователя
    if not user_qsos.exists():
        # Если нет данных, показываем пустую страницу
        return render(request, 'achievements_base.html', {
            'total_qso': 0,
            'bands': {},
            'available_bands': [],
            'band_order': ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm', '23cm', '13cm'],
            'modes': {},
            'unique_callsigns': 0,
            'r150s_count': 0,
            'dxcc_count': 0,
            'state_count': 0,
            'cqz_count': 0,
            'ituz_count': 0,
            'grids_count': 0,
            'lotw_count': 0,
            'today_qso': 0,
            'week_qso': 0,
            'month_qso': 0,
            'most_active_date': None,
            'achievements': [],
            'my_callsigns': [],
        })

    # Оптимизированная загрузка всех статистических данных
    # Основная статистика
    total_qso = user_qsos.count()

    # Статистика по диапазонам (оптимизировано)
    band_order = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
    band_counts = dict(user_qsos.filter(band__isnull=False, band__gt='')
                       .values('band').annotate(count=Count('id')).values_list('band', 'count'))
    
    # Уникальные диапазоны для фильтров
    available_bands = list(user_qsos.filter(band__isnull=False, band__gt='')
                          .values_list('band', flat=True).distinct().order_by('band'))

    # Статистика по модуляциям (оптимизировано)
    mode_counts = dict(user_qsos.filter(mode__isnull=False, mode__gt='')
                       .values('mode').annotate(count=Count('id')).values_list('mode', 'count'))

    # Оптимизированные подсчеты уникальных значений
    unique_callsigns = user_qsos.filter(callsign__isnull=False, callsign__gt='').values('callsign').distinct().count()
    r150s_count = user_qsos.filter(r150s__isnull=False, r150s__gt='').values('r150s').distinct().count()
    dxcc_count = user_qsos.filter(dxcc__isnull=False, dxcc__gt='').values('dxcc').distinct().count()
    state_count = user_qsos.filter(state__isnull=False, state__gt='').values('state').distinct().count()
    cqz_count = user_qsos.filter(cqz__isnull=False).values('cqz').distinct().count()
    ituz_count = user_qsos.filter(ituz__isnull=False).values('ituz').distinct().count()
    grids_count = user_qsos.filter(gridsquare__isnull=False, gridsquare__gt='').values('gridsquare').distinct().count()
    
    # Уникальные мои позывные
    my_callsigns = list(user_qsos.filter(my_callsign__isnull=False, my_callsign__gt='')
                       .values_list('my_callsign', flat=True).distinct().order_by('my_callsign'))

    # LoTW подтверждения
    lotw_count = user_qsos.filter(lotw='Y').count()

    # Статистика по датам (оптимизировано)
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Получаем всю датовую статистику одним запросом
    date_stats = user_qsos.aggregate(
        today_qso=Count('id', filter=Q(date=today)),
        week_qso=Count('id', filter=Q(date__gte=week_ago)),
        month_qso=Count('id', filter=Q(date__gte=month_ago))
    )
    
    today_qso = date_stats['today_qso']
    week_qso = date_stats['week_qso']
    month_qso = date_stats['month_qso']

    # Самая активная дата (оптимизировано)
    most_active_date = user_qsos.values('date').annotate(
        count=Count('id')
    ).order_by('-count').first()

    # Достижения (awards)
    achievements = []

    # 100 QSO
    if total_qso >= 100:
        achievements.append({
            'title': 'Новичок',
            'description': 'Зарегистрировано 100+ QSO',
            'icon': '🎯',
            'unlocked': True
        })

    # 500 QSO
    if total_qso >= 500:
        achievements.append({
            'title': 'Опытный',
            'description': 'Зарегистрировано 500+ QSO',
            'icon': '⭐',
            'unlocked': True
        })

    # 1000 QSO
    if total_qso >= 1000:
        achievements.append({
            'title': 'Мастер',
            'description': 'Зарегистрировано 1000+ QSO',
            'icon': '🏆',
            'unlocked': True
        })

    # 10 диапазонов
    if len(band_counts) >= 10:
        achievements.append({
            'title': 'Разведчик',
            'description': 'Связи на 10+ диапазонах',
            'icon': '📡',
            'unlocked': True
        })

    # 5 видов модуляций
    if len(mode_counts) >= 5:
        achievements.append({
            'title': 'Универсал',
            'description': 'Связи на 5+ видах модуляции',
            'icon': '🎛️',
            'unlocked': True
        })

    # 50 стран Р-150-С
    if r150s_count >= 50:
        achievements.append({
            'title': 'Охотник за DX',
            'description': 'Связи с 50+ странами Р-150-С',
            'icon': '🌍',
            'unlocked': True
        })

    # 100 стран Р-150-С
    if r150s_count >= 100:
        achievements.append({
            'title': 'Патриот',
            'description': 'Связи со 100+ странами Р-150-С',
            'icon': '🎖️',
            'unlocked': True
        })

    # LoTW подтверждения
    if lotw_count >= 10:
        achievements.append({
            'title': 'Цифровой оператор',
            'description': '10+ подтверждений LoTW',
            'icon': '💻',
            'unlocked': True
        })

    # Активность за неделю
    if week_qso >= 50:
        achievements.append({
            'title': 'В эфире',
            'description': '50+ связей за неделю',
            'icon': '📻',
            'unlocked': True
        })

    # === Награды QO-100 (оптимизировано) ===
    # QO-100 статистика с LoTW (оптимизированный запрос)
    qo100_lotw_stats = user_qsos.filter(sat_name='QO-100', lotw='Y').aggregate(
        states=Count('state', filter=Q(state__isnull=False, state__gt='')),
        countries=Count('r150s', filter=Q(r150s__isnull=False, r150s__gt='')),
        grids=Count('gridsquare', filter=Q(gridsquare__isnull=False, gridsquare__gt='')),
        callsigns=Count('callsign', filter=Q(callsign__isnull=False, callsign__gt=''))
    )

    # QO-100 общая статистика
    qo100_all_callsigns = user_qsos.filter(sat_name='QO-100').values('callsign').distinct().count()

    # Награды QO-100
    if qo100_lotw_stats['states'] >= 25:
        achievements.append({
            'title': 'W-QO100-R',
            'description': '25+ регионов РФ через QO-100 (LoTW)',
            'icon': '🗺️',
            'unlocked': True
        })

    if qo100_lotw_stats['states'] >= 30:
        achievements.append({
            'title': 'W-QO100-PROFI',
            'description': '30+ регионов РФ через QO-100 (LoTW)',
            'icon': '🎓',
            'unlocked': True
        })

    if qo100_lotw_stats['countries'] >= 100:
        achievements.append({
            'title': 'W-QO100-C',
            'description': '100+ стран через QO-100 (LoTW)',
            'icon': '🌐',
            'unlocked': True
        })

    if qo100_lotw_stats['grids'] >= 500:
        achievements.append({
            'title': 'W-QO100-L',
            'description': '500+ QTH локаторов через QO-100 (LoTW)',
            'icon': '📍',
            'unlocked': True
        })

    if qo100_lotw_stats['callsigns'] >= 1000:
        achievements.append({
            'title': 'W-QO100-U',
            'description': '1000+ позывных через QO-100 (LoTW)',
            'icon': '📡',
            'unlocked': True
        })

    if qo100_all_callsigns >= 1000:
        achievements.append({
            'title': 'W-QO100-B',
            'description': '1000+ связей через QO-100',
            'icon': '🛰️',
            'unlocked': True
        })

    # Формируем данные для шаблона
    context_data = {
        'total_qso': total_qso,
        'bands': band_counts,
        'available_bands': available_bands,
        'band_order': band_order,
        'modes': mode_counts,
        'unique_callsigns': unique_callsigns,
        'r150s_count': r150s_count,
        'dxcc_count': dxcc_count,
        'state_count': state_count,
        'cqz_count': cqz_count,
        'ituz_count': ituz_count,
        'grids_count': grids_count,
        'lotw_count': lotw_count,
        'today_qso': today_qso,
        'week_qso': week_qso,
        'month_qso': month_qso,
        'most_active_date': most_active_date,
        'achievements': achievements,
        'my_callsigns': my_callsigns,
    }

    # Кэшируем результат на 5 минут
    cache.set(cache_key, context_data, 300)
    
    return render(request, 'achievements_base.html', context_data)



def user_achievements(request):
    """
    Страница с наградами всех пользователей
    """
    from django.contrib.auth.models import User
    from datetime import timedelta
    from django.utils import timezone

    # Проверяем, не заблокирован ли пользователь (если авторизован)
    if request.user.is_authenticated:
        is_blocked, reason = check_user_blocked(request.user)
        if is_blocked:
            return render(request, 'blocked.html', {'reason': reason})

    # Получаем всех пользователей с QSO
    users_with_qso = User.objects.filter(
        qsos__isnull=False
    ).distinct().order_by('username')

    user_achievements_list = []

    for user in users_with_qso:
        # Получаем позывной из профиля
        try:
            profile = user.radio_profile
            callsign = profile.callsign or user.username
        except Exception:
            callsign = user.username

        # Основная статистика
        total_qso = QSO.objects.filter(user=user).count()
        if total_qso == 0:
            continue

        # Диапазоны
        bands = QSO.objects.filter(user=user).exclude(band__isnull=True).exclude(band='').values('band').distinct().count()

        # Модуляции
        modes = QSO.objects.filter(user=user).exclude(mode__isnull=True).values('mode').distinct().count()

        # Страны Р-150-С
        r150s_count = QSO.objects.filter(user=user).exclude(r150s__isnull=True).exclude(r150s='').values('r150s').distinct().count()

        # Регионы России
        states = QSO.objects.filter(user=user).exclude(state__isnull=True).exclude(state='').values('state').distinct().count()

        # LoTW подтверждения
        lotw_count = QSO.objects.filter(user=user, lotw='Y').count()

        # Достижения (awards)
        achievements = []

        # 100+ QSO
        if total_qso >= 100:
            achievements.append({'title': 'Новичок', 'icon': '🎯'})
        # 500+ QSO
        if total_qso >= 500:
            achievements.append({'title': 'Опытный', 'icon': '⭐'})
        # 1000+ QSO
        if total_qso >= 1000:
            achievements.append({'title': 'Мастер', 'icon': '🏆'})

        # 10+ диапазонов
        if bands >= 10:
            achievements.append({'title': 'Разведчик', 'icon': '📡'})

        # 5+ модуляций
        if modes >= 5:
            achievements.append({'title': 'Универсал', 'icon': '🎛️'})

        # 50+ стран Р-150-С
        if r150s_count >= 50:
            achievements.append({'title': 'Охотник за DX', 'icon': '🌍'})

        # 100+ стран Р-150-С
        if r150s_count >= 100:
            achievements.append({'title': 'Патриот', 'icon': '🎖️'})

        # LoTW подтверждения
        if lotw_count >= 10:
            achievements.append({'title': 'Цифровой оператор', 'icon': '💻'})

        # QO-100 награды
        qo100_all_callsigns = QSO.objects.filter(user=user, sat_name='QO-100').values('callsign').distinct().count()
        qo100_lotw_callsigns = QSO.objects.filter(user=user, sat_name='QO-100', lotw='Y').values('callsign').distinct().count()

        if qo100_lotw_callsigns >= 1000:
            achievements.append({'title': 'W-QO100-U', 'icon': '📡'})
        if qo100_lotw_callsigns >= 500:
            achievements.append({'title': 'W-QO100-L', 'icon': '📍'})
        if qo100_lotw_callsigns >= 100:
            achievements.append({'title': 'W-QO100-C', 'icon': '🌐'})
        if qo100_lotw_callsigns >= 30:
            achievements.append({'title': 'W-QO100-PROFI', 'icon': '🎓'})
        if qo100_lotw_callsigns >= 25:
            achievements.append({'title': 'W-QO100-R', 'icon': '🗺️'})

        if qo100_all_callsigns >= 1000:
            achievements.append({'title': 'W-QO100-B', 'icon': '🛰️'})

        user_achievements_list.append({
            'user_id': user.id,
            'username': user.username,
            'callsign': callsign,
            'total_qso': total_qso,
            'bands': bands,
            'modes': modes,
            'r150s_count': r150s_count,
            'states': states,
            'lotw_count': lotw_count,
            'achievements': achievements,
            'achievement_count': len(achievements),
        })

    # Сортируем по количеству наград (DESC), затем по QSO (DESC)
    user_achievements_list.sort(key=lambda x: (x['achievement_count'], x['total_qso']), reverse=True)

    # Статистика платформы
    total_users = users_with_qso.count()
    total_qso_all = QSO.objects.count()
    total_qow_lotw = QSO.objects.filter(lotw='Y').count()

