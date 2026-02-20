# QSO Search Form for QRZ.com (by owner_callsign)

## ✅ What's ready:

1. **API updated** - uses `owner_callsign` to get user_id from RadioProfile
2. **Form for QRZ.com** - with hidden `owner_callsign` field
3. **Test page** - for testing functionality

## 📋 How it works:

```
User on QRZ.com (page R3LO)
    ↓
Enters their callsign (e.g., GJ0KYZ)
    ↓
API gets user_id by owner_callsign="R3LO" from RadioProfile
    ↓
Searches QSO where user_id=1 AND callsign="GJ0KYZ"
    ↓
Returns all QSO (rows=my_callsign, columns=modes)
```

## 🧪 Testing:

Open in browser:
```
http://127.0.0.1:8080/test_qrz_user_en.html
```

**Test 1:**
- Owner Callsign: `R3LO`
- Search Callsign: `GJ0KYZ`
- Result: QSO R3LO with GJ0KYZ (10 contacts)

**Test 2:**
- Owner Callsign: `RA3DNC`
- Search Callsign: `GJ0KYZ`
- Result: QSO RA3DNC with GJ0KYZ (20 contacts) - **different user_id!**

## 📝 Installation on QRZ.com:

1. Open file `QRZ_COM_FORM_FOR_USER.md`

2. Change this line:
   ```javascript
   const OWNER_CALLSIGN = 'R3LO';  // REPLACE WITH YOUR CALLSIGN
   ```

3. Copy all HTML/JavaScript code

4. Paste into your QRZ.com profile page in the "Bio" field

## 🔗 API Endpoint:

```
GET /api/v1/public/qso-search/?owner_callsign={owner}&search_callsign={search}
```

**Parameters:**
- `owner_callsign` - page owner's callsign (e.g., "R3LO")
- `search_callsign` - correspondent's callsign (e.g., "GJ0KYZ")

**Response:**
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

## ✅ Verified:

- ✅ API uses RadioProfile to get user_id
- ✅ Filtering by user_id works (R3LO and RA3DNC return different results)
- ✅ CORS configured for work on qrz.com
- ✅ Form works with new parameters
- ✅ Form is in English

## 📁 Files:

- `QRZ_COM_FORM_FOR_USER.md` - form code for QRZ.com (English)
- `test_qrz_user_en.html` - test page (English)
- `tlog/views/rest_api.py` - updated API (PublicQSOSearchAPIView)

## 🌐 Form Text (English):

- Title: "Check QSO in my log"
- Input placeholder: "Enter your callsign"
- Button: "Search"
- Loading: "Searching..."
- Not found: "No QSO found for callsign X in log of Y"
- Table headers: "My Callsign", [Mode names], "Total"
