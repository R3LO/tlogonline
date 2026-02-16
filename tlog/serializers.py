"""
Serializers для Django REST Framework
"""
from rest_framework import serializers
from .models import QSO, RadioProfile


class QSOSerializer(serializers.ModelSerializer):
    """
    Serializer для модели QSO
    """
    class Meta:
        model = QSO
        fields = [
            'id', 'date', 'time', 'my_callsign', 'callsign',
            'frequency', 'band', 'mode', 'rst_sent', 'rst_rcvd',
            'my_gridsquare', 'gridsquare', 'continent', 'state',
            'prop_mode', 'sat_name', 'r150s', 'dxcc', 'cqz', 'ituz',
            'app_lotw_rxqsl', 'vucc_grids', 'iota', 'lotw', 'paper_qsl',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RadioProfileSerializer(serializers.ModelSerializer):
    """
    Serializer для модели RadioProfile
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = RadioProfile
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'callsign', 'qth', 'my_gridsquare',
            'lotw_user', 'lotw_chk_pass', 'lotw_lastsync',
            'my_callsigns', 'is_blocked', 'blocked_reason', 'blocked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'username', 'email', 'first_name', 'last_name',
            'created_at', 'updated_at', 'lotw_chk_pass', 'lotw_lastsync',
            'is_blocked', 'blocked_reason', 'blocked_at'
        ]


class QSOStatsSerializer(serializers.Serializer):
    """
    Serializer для статистики QSO
    """
    total_qso = serializers.IntegerField()
    unique_callsigns = serializers.IntegerField()
    dxcc_count = serializers.IntegerField()
    band_statistics = serializers.DictField()
    mode_statistics = serializers.DictField()
    year_statistics = serializers.DictField()
