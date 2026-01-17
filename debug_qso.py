import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tlog.models import QSO

callsign = 'R3LO'
qs = QSO.objects.filter(my_callsign=callsign)
print(f'Total QSO for {callsign}: {qs.count()}')

if qs.count() > 0:
    modes = qs.values_list('mode', flat=True).distinct()
    print(f'Modes: {list(modes)}')

    freqs = list(qs.values_list('frequency', flat=True)[:20])
    print(f'Frequencies: {freqs}')

    bands = qs.values_list('band', flat=True).distinct()
    print(f'Bands: {list(bands)}')

    # Test matrix
    print('\n--- Testing matrix ---')
    modes_list = ['CW', 'SSB', 'FT8', 'FT4']
    bands_list = ['160m', '80m', '40m', '20m', '10m', '2m']
    band_ranges = {
        '160m': (1.8, 2.0), '80m': (3.5, 4.0), '40m': (7.0, 7.3), '20m': (14.0, 14.35),
        '10m': (28.0, 29.7), '2m': (144.0, 148.0),
    }

    for mode in modes_list:
        for band in bands_list:
            if band in band_ranges:
                min_freq, max_freq = band_ranges[band]
                count = qs.filter(mode=mode, frequency__gte=min_freq, frequency__lte=max_freq).count()
                print(f'{mode}/{band}: {count} QSO')