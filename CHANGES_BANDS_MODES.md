# Changes: Bands and Modes Display

## What Changed

### 1. **API Structure Updated**

**Before:**
```json
{
    "found": true,
    "owner_callsign": "R3LO",
    "search_callsign": "GJ0KYZ",
    "results": [
        {
            "my_callsign": "R3LO",
            "modes": {
                "CW": 2,
                "FT8": 6,
                "FT4": 2
            }
        }
    ]
}
```

**After:**
```json
{
    "found": true,
    "owner_callsign": "R3LO",
    "search_callsign": "GJ0KYZ",
    "results": [
        {
            "my_callsign": "R3LO",
            "bands": {
                "17M": {
                    "CW": 2,
                    "FT8": 3
                },
                "40M": {
                    "FT4": 1,
                    "FT8": 1
                },
                "20M": {
                    "FT4": 1,
                    "FT8": 1
                },
                "30M": {
                    "FT8": 1
                }
            }
        }
    ]
}
```

### 2. **Table Structure**

**Before:**
| My Callsign | CW | FT8 | FT4 | Total |
|-------------|----|-----|-----|-------|
| R3LO | 2 | 6 | 2 | 10 |

**After:**
| My Callsign | 17M | 20M | 30M | 40M | Total |
|-------------|-----|-----|-----|-----|-------|
| R3LO | CW:2<br>FT8:3 | FT4:1<br>FT8:1 | FT8:1 | FT4:1<br>FT8:1 | 10 |

### 3. **Satellite Support**

If QSO has `sat_name`, it will be displayed as:
- Column header: `SAT` with satellite name in smaller text
- Example: `SAT<br><small>FO-29</small>`

### 4. **Removed Callsign Validation**

The regex validation for callsign format has been removed. Users can now enter any text in the search field.

## Sorting Rules

1. **Bands are sorted numerically** (e.g., 160m, 80m, 40m, 20m, 17m, 15m, 10m)
2. **Satellite bands come last**, sorted alphabetically by name
3. **Modes are sorted alphabetically** within each band

## API Endpoint

```
GET /api/v1/public/qso-search/?owner_callsign={owner}&search_callsign={search}
```

## Files Updated

1. `tlog/views/rest_api.py` - PublicQSOSearchAPIView
2. `QRZ_COM_FORM_FOR_USER.md` - Form for QRZ.com
3. `test_qrz_user_en.html` - Test page
