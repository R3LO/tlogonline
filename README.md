# Ham Radio Website - Django 5

Modern platform for ham radio operators with callsign registration, QTH locators, QSO logging and ADIF file upload.

## Features

- Django 5.0.4 + DRF
- Callsign registration (mandatory)
- QTH locator support (e.g., KO85UU)
- QSO logging with full details
- ADIF file upload and parsing
- Statistics by mode and band
- Personal dashboard
- REST API
- Admin panel

## Quick Start

```bash
pip install -r requirements_minimal.txt
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py createsuperuser
python create_test_data_ham.py
python manage.py runserver 0.0.0.0:8000
```

## Test Accounts

**Admin:**
- Login: admin
- Password: admin123

**Ham Radio Operator:**
- Login: test_ham_operator
- Password: testpass123
- Callsign: RA9XYZ
- QTH: LO91AA

## Pages

- Homepage: http://localhost:8000/
- Registration: http://localhost:8000/register/
- Login: http://localhost:8000/login/
- Dashboard: http://localhost:8000/dashboard/
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Supported Modes

SSB, CW, FM, AM, FT8, RTTY, SSTV, PSK31, PSK63, JT65, JT9, OTHER

## Supported Bands

160m, 80m, 40m, 20m, 15m, 10m, 6m, 2m, 70cm, 23cm, 13cm, 9cm, 6cm, 3cm

## Testing

```bash
python final_test_simple.py
```

All tests should pass:
- Ham registration with callsigns: WORKING
- Authentication system: WORKING
- Personal dashboard: WORKING
- API endpoints: WORKING
- QSO statistics: WORKING
- Callsign and QTH locator support: WORKING

## API Examples

### Register Ham Radio Operator
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_ham",
    "email": "ham@example.com", 
    "password": "password123",
    "password_confirm": "password123",
    "callsign": "RA3DEF",
    "qth_locator": "LO85AA",
    "city": "St.Petersburg",
    "country": "Russia",
    "radio_license_class": "1"
  }'
```

### Create QSO Record
```bash
curl -X POST http://localhost:8000/api/qso/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_id" \
  -d '{
    "my_callsign": "UA1ABC",
    "counterpart_callsign": "RA3DEF",
    "frequency": 14.205,
    "mode": "SSB",
    "signal_report": "59",
    "notes": "Great contact!"
  }'
```

### Upload ADIF File
```bash
curl -X POST http://localhost:8000/api/adif-uploads/ \
  -H "Cookie: sessionid=your_session_id" \
  -F "file=@your_log.adi"
```

## Models

### RadioProfile
- callsign (unique, required)
- qth_locator (e.g., KO85UU)
- radio_license_class
- city, country
- is_verified

### QSO
- my_callsign, counterpart_callsign
- my_qth_locator, counterpart_qth_locator
- frequency (MHz)
- mode (SSB, CW, FM, AM, FT8, etc.)
- date_time
- signal_report (RST)
- notes

### ADIFUpload
- file upload
- processed status
- qso_count
- error_message

## Database Statistics

After running test data creation:
- Total users: 3
- Total ham profiles: 3  
- Total QSO records: 764+

## Website Status

HAM RADIO WEBSITE IS READY FOR USE!

73! Best 73 and good luck with your DX contacts! 📡