import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Test the matrix
from tlog.models import QSO

callsign = 'R3LO'
qs = QSO.objects.filter(my_callsign=callsign)
print(f'Total QSO for {callsign}: {qs.count()}')

bands = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm', '23cm', '13cm']
modes = ['CW', 'SSB', 'FT8', 'FT4', 'RTTY', 'SSTV', 'MFSK', 'JT65', 'JT9', 'PSK31', 'AM', 'FM', 'DIG']
band_ranges = {
    '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '30m': (10.1, 10.15),
    '20m': (14.0, 14.35), '17m': (18.068, 18.168), '15m': (21.0, 21.45),
    '12m': (24.89, 24.99), '10m': (28.0, 29.7), '6m': (50.0, 54.0),
    '2m': (144.0, 148.0), '70cm': (420.0, 450.0), '23cm': (1240.0, 1300.0),
    '13cm': (2300.0, 2450.0),
}

from django.db.models import Q

# Build matrix
matrix = []
for mode in modes:
    row = [mode]
    for band in bands:
        count = qs.filter(
            Q(mode__iexact=mode) &
            (Q(band=band) | Q(frequency__gte=band_ranges[band][0], frequency__lte=band_ranges[band][1]))
        ).count()
        row.append(count > 0)
    matrix.append(row)

print('\nMatrix:')
for row in matrix:
    has_any = any(row[1:])  # Skip mode name
    if has_any:
        print(f'{row[0]}: ', end='')
        for i, band in enumerate(bands):
            if row[i + 1]:
                print(f'{band}=OK ', end='')
        print()