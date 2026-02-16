"""
REST API ViewSet с использованием Django REST Framework и Basic Authentication
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
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
