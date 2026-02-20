"""
REST API ViewSet с использованием Django REST Framework и Basic Authentication
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render
from django.db.models import Count, Q
from collections import Counter

from ..models import QSO, RadioProfile
from ..serializers import QSOSerializer, RadioProfileSerializer, QSOStatsSerializer


class QSOViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с QSO
    Позволяет просматривать, создавать, обновлять и удалять QSO
    """
    serializer_class = QSOSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только QSO текущего пользователя
        """
        return QSO.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        При создании QSO автоматически привязываем его к текущему пользователю
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Получить статистику QSO текущего пользователя
        """
        user_qso = self.get_queryset()

        total_qso = user_qso.count()
        unique_callsigns = user_qso.values('callsign').distinct().count()
        dxcc_count = user_qso.exclude(dxcc__isnull=True).exclude(dxcc='').values('dxcc').distinct().count()

        # Статистика по диапазонам
        bands = user_qso.values_list('band', flat=True)
        band_stats = dict(Counter(bands))

        # Статистика по модуляции
        modes = user_qso.values_list('mode', flat=True)
        mode_stats = dict(Counter(modes))

        # Статистика по годам
        years = [qso.date.year for qso in user_qso if qso.date]
        year_stats = dict(Counter(years))

        stats_data = {
            'total_qso': total_qso,
            'unique_callsigns': unique_callsigns,
            'dxcc_count': dxcc_count,
            'band_statistics': band_stats,
            'mode_statistics': mode_stats,
            'year_statistics': year_stats,
        }

        serializer = QSOStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Поиск QSO по позывному корреспондента
        """
        callsign = request.query_params.get('callsign', '').upper()
        if not callsign:
            return Response(
                {'error': 'Параметр callsign обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        qsos = self.get_queryset().filter(callsign__icontains=callsign)
        serializer = self.get_serializer(qsos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_band(self, request):
        """
        Получить QSO по диапазону
        """
        band = request.query_params.get('band', '').upper()
        if not band:
            return Response(
                {'error': 'Параметр band обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        qsos = self.get_queryset().filter(band__icontains=band)
        serializer = self.get_serializer(qsos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_grid(self, request):
        """
        Получить QSO по QTH локатору (gridsquare)
        """
        grid = request.query_params.get('grid', '').upper()
        if not grid:
            return Response(
                {'error': 'Параметр grid обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        qsos = self.get_queryset().filter(gridsquare__icontains=grid)
        serializer = self.get_serializer(qsos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_lotw(self, request):
        """
        Получить QSO подтверждённые через LoTW
        Сортировка по дате получения подтверждения (app_lotw_rxqsl)
        """
        qsos = self.get_queryset().filter(lotw='Y').order_by('-app_lotw_rxqsl')
        serializer = self.get_serializer(qsos, many=True)
        return Response(serializer.data)


class ProfileAPIView(APIView):
    """
    API для получения профиля текущего пользователя
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Получить профиль текущего пользователя
        """
        try:
            profile = request.user.radio_profile
            serializer = RadioProfileSerializer(profile)
            return Response(serializer.data)
        except RadioProfile.DoesNotExist:
            return Response(
                {'error': 'Профиль не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request):
        """
        Обновить профиль текущего пользователя
        """
        try:
            profile = request.user.radio_profile
            serializer = RadioProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except RadioProfile.DoesNotExist:
            return Response(
                {'error': 'Профиль не найден'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserInfoAPIView(APIView):
    """
    API для получения базовой информации о пользователе
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Получить базовую информацию о текущем пользователе
        """
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
        }
        return Response(data)


class PublicQSOSearchAPIView(APIView):
    """
    Публичный API для поиска QSO по позывному (без аутентификации)
    Для использования на внешних сайтах (например, qrz.com)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Поиск QSO по позывному корреспондента (callsign) и позывному владельца (owner_callsign)
        owner_callsign используется для получения user_id из RadioProfile
        Возвращает данные в формате: строки = my_callsign, колонки = band/sat_name, ячейки = mode:count

        Параметры:
        - owner_callsign: позывной владельца страницы (например, "R3LO") - используется для получения user_id из RadioProfile (обязательный)
        - search_callsign: позывной для поиска корреспондента (обязательный)

        Ответ:
        {
            "found": true,
            "owner_callsign": "R3LO",
            "search_callsign": "UA1AAA",
            "results": [
                {
                    "my_callsign": "R3LO",
                    "bands": {
                        "160m": {"CW": 2, "FT8": 1},
                        "80m": {"SSB": 3},
                        "20m": {"FT8": 5},
                        "SAT": {"FO-29": {"CW": 1}}
                    }
                }
            ]
        }
        """
        owner_callsign = request.query_params.get('owner_callsign', '').strip().upper()
        search_callsign = request.query_params.get('search_callsign', '').strip().upper()

        if not owner_callsign:
            return Response(
                {
                    'found': False,
                    'error': 'owner_callsign parameter is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not search_callsign:
            return Response(
                {
                    'found': False,
                    'error': 'search_callsign parameter is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ищем RadioProfile по позывному владельца
        try:
            radio_profile = RadioProfile.objects.get(callsign__iexact=owner_callsign)
            user = radio_profile.user
        except RadioProfile.DoesNotExist:
            return Response({
                'found': False,
                'error': f'Profile with callsign {owner_callsign} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Ищем QSO с указанным search_callsign для конкретного пользователя
        qsos = QSO.objects.filter(
            callsign__iexact=search_callsign,
            user=user
        ).select_related('user')

        if not qsos.exists():
            return Response({
                'found': False,
                'owner_callsign': owner_callsign,
                'search_callsign': search_callsign,
                'message': 'Not found'
            })

        # Группируем по my_callsign, затем по band/sat_name, затем по mode
        results = {}
        for qso in qsos:
            my_callsign = qso.my_callsign or 'UNKNOWN'
            mode = qso.mode or 'UNKNOWN'

            # Определяем ключ для диапазона/спутника
            if qso.sat_name:
                band_key = f"SAT:{qso.sat_name}"
            else:
                band_key = qso.band or 'UNKNOWN'

            if my_callsign not in results:
                results[my_callsign] = {}

            if band_key not in results[my_callsign]:
                results[my_callsign][band_key] = {}

            if mode not in results[my_callsign][band_key]:
                results[my_callsign][band_key][mode] = 0

            results[my_callsign][band_key][mode] += 1

        # Преобразуем в список
        formatted_results = [
            {
                'my_callsign': my_callsign,
                'bands': bands
            }
            for my_callsign, bands in results.items()
        ]

        # Сортируем по количеству QSO (по убыванию)
        formatted_results.sort(
            key=lambda x: sum(
                sum(modes.values())
                for modes in x['bands'].values()
            ),
            reverse=True
        )

        return Response({
            'found': True,
            'owner_callsign': owner_callsign,
            'search_callsign': search_callsign,
            'results': formatted_results
        })


def public_qso_search_html(request):
    """
    HTML форма для поиска QSO (без JavaScript)
    Для использования на QRZ.com и других сайтах, блокирующих скрипты

    Параметры:
    - owner_callsign: позывной владельца (обязательный)
    - search_callsign: позывной для поиска (обязательный)
    """
    owner_callsign = request.GET.get('owner_callsign', '').strip().upper()
    search_callsign = request.GET.get('search_callsign', '').strip().upper()

    results = []
    found = False
    error = None
    all_bands = []

    if owner_callsign and search_callsign:
        # Ищем RadioProfile по позывному владельца
        try:
            radio_profile = RadioProfile.objects.get(callsign__iexact=owner_callsign)
            user = radio_profile.user

            # Ищем QSO
            qsos = QSO.objects.filter(
                callsign__iexact=search_callsign,
                user=user
            ).select_related('user')

            if qsos.exists():
                found = True

                # Группируем по my_callsign, затем по band/sat_name, затем по mode
                results_dict = {}
                for qso in qsos:
                    my_callsign = qso.my_callsign or 'UNKNOWN'
                    mode = qso.mode or 'UNKNOWN'

                    # Определяем ключ для диапазона/спутника
                    if qso.sat_name:
                        band_key = f"SAT:{qso.sat_name}"
                    else:
                        band_key = qso.band or 'UNKNOWN'

                    if my_callsign not in results_dict:
                        results_dict[my_callsign] = {}

                    if band_key not in results_dict[my_callsign]:
                        results_dict[my_callsign][band_key] = {}

                    if mode not in results_dict[my_callsign][band_key]:
                        results_dict[my_callsign][band_key][mode] = 0

                    results_dict[my_callsign][band_key][mode] += 1

                # Собираем все уникальные bands
                all_bands_set = set()
                for my_callsign, bands in results_dict.items():
                    all_bands_set.update(bands.keys())

                # Сортируем bands
                def sort_bands(band):
                    if band.startswith('SAT:'):
                        return (2, band[4:])
                    num = band.replace('m', '')
                    try:
                        return (0, int(num))
                    except ValueError:
                        return (1, band)

                all_bands = sorted(all_bands_set, key=sort_bands)

                # Преобразуем в список и сортируем
                results = []
                for my_callsign, bands in results_dict.items():
                    total = sum(sum(modes.values()) for modes in bands.values())

                    # Создаем список для каждого band с modes
                    bands_data = []
                    for band in all_bands:
                        if band in bands:
                            modes_list = sorted(bands[band].keys())
                            bands_data.append({
                                'band': band,
                                'modes': modes_list
                            })
                        else:
                            bands_data.append({
                                'band': band,
                                'modes': []
                            })

                    results.append({
                        'my_callsign': my_callsign,
                        'bands_data': bands_data,
                        'total': total
                    })

                results.sort(key=lambda x: x['total'], reverse=True)
            else:
                found = False
        except RadioProfile.DoesNotExist:
            error = f'Profile with callsign {owner_callsign} not found'
        except Exception as e:
            error = str(e)

    return render(request, 'public_qso_search.html', {
        'owner_callsign': owner_callsign,
        'search_callsign': search_callsign,
        'found': found,
        'results': results,
        'all_bands': all_bands,
        'error': error,
    })
