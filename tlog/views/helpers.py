"""
Вспомогательные функции для представлений
"""
from ..models import QSO


def get_band_from_frequency(frequency):
    """
    Определяет диапазон по частоте
    """
    if not frequency:
        return None

    # Диапазоны любительских частот
    band_ranges = [
        ('160m', 1.8, 2.0),
        ('80m', 3.5, 4.0),
        ('60m', 5.33, 5.4),
        ('40m', 7.0, 7.3),
        ('30m', 10.1, 10.15),
        ('20m', 14.0, 14.35),
        ('17m', 18.068, 18.168),
        ('15m', 21.0, 21.45),
        ('12m', 24.89, 24.99),
        ('10m', 28.0, 29.7),
        ('6m', 50.0, 54.0),
        ('4m', 70.0, 70.5),
        ('2m', 144.0, 148.0),
        ('1.25m', 222.0, 225.0),
        ('70cm', 420.0, 450.0),
        ('33cm', 902.0, 928.0),
        ('23cm', 1240.0, 1300.0),
        ('13cm', 2300.0, 2450.0),
        ('9cm', 3300.0, 3500.0),
        ('6cm', 5650.0, 5850.0),
        ('3cm', 10000.0, 10500.0),
        ('1.2cm', 24000.0, 24250.0),
        ('6mm', 47000.0, 47200.0),
    ]

    for band, min_freq, max_freq in band_ranges:
        if min_freq <= frequency <= max_freq:
            return band

    return None


def generate_adif_content(qso_queryset):
    """
    Генерирует содержимое ADIF файла из QuerySet QSO
    """
    adif_lines = []

    # ADIF заголовок
    adif_lines.append("<ADIF_VER:5>3.1.0")
    adif_lines.append("<PROGRAMID:8>TLog")
    adif_lines.append("<EOH>")
    adif_lines.append("")

    # ADIF записи QSO
    for qso in qso_queryset:
        adif_lines.append(f"<QSO_DATE:8>{qso.date.strftime('%Y%m%d')}")
        adif_lines.append(f"<TIME_ON:4>{qso.time.strftime('%H%M')}")
        adif_lines.append(f"<CALL:{len(qso.callsign)}>{qso.callsign}")
        if qso.my_callsign:
            adif_lines.append(f"<MY_CALL:{len(qso.my_callsign)}>{qso.my_callsign}")
        if qso.band:
            adif_lines.append(f"<BAND:{len(qso.band)}>{qso.band}")
        if qso.frequency:
            adif_lines.append(f"<FREQ:11>{qso.frequency:.6f}")
        if qso.mode:
            adif_lines.append(f"<MODE:{len(qso.mode)}>{qso.mode}")
        if qso.rst_sent:
            adif_lines.append(f"<RST_SENT:{len(qso.rst_sent)}>{qso.rst_sent}")
        if qso.rst_rcvd:
            adif_lines.append(f"<RST_RCVD:{len(qso.rst_rcvd)}>{qso.rst_rcvd}")
        if qso.my_gridsquare:
            adif_lines.append(f"<MY_GRIDSQUARE:{len(qso.my_gridsquare)}>{qso.my_gridsquare}")
        if qso.gridsquare:
            adif_lines.append(f"<GRIDSQUARE:{len(qso.gridsquare)}>{qso.gridsquare}")
        if qso.prop_mode:
            adif_lines.append(f"<PROP_MODE:{len(qso.prop_mode)}>{qso.prop_mode}")
        if qso.sat_name:
            adif_lines.append(f"<SAT_NAME:{len(qso.sat_name)}>{qso.sat_name}")
        if qso.cqz:
            adif_lines.append(f"<CQZ:{len(str(qso.cqz))}>{qso.cqz}")
        if qso.ituz:
            adif_lines.append(f"<ITUZ:{len(str(qso.ituz))}>{qso.ituz}")
        if qso.continent:
            adif_lines.append(f"<CONT:{len(qso.continent)}>{qso.continent}")
        if qso.r150s:
            adif_lines.append(f"<COUNTRY:{len(qso.r150s)}>{qso.r150s}")
        if qso.dxcc:
            adif_lines.append(f"<DXCC:{len(qso.dxcc)}>{qso.dxcc}")
        if qso.state:
            adif_lines.append(f"<STATE:{len(qso.state)}>{qso.state}")
        if qso.lotw:
            adif_lines.append(f"<LOTW_QSLR:{len(qso.lotw)}>{qso.lotw}")
        adif_lines.append("<EOR>")
        adif_lines.append("")

    return '\n'.join(adif_lines)
