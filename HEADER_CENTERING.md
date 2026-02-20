# Table Header Centering

## Changes Made

### Centered Text in Table Headers

**CSS Updated:**
```css
#tlog-result-table th {
    background: #0066cc;
    color: white;
    font-weight: bold;
    text-align: center;  /* New: centered text */
}
```

## Table Appearance

### Before:
| My Callsign | 17M | 20M | 30M | 40M | Total |
|-------------|-----|-----|-----|-----|-------|
| R3LO | [CW] [FT8] | [FT4] [FT8] | [FT8] | [FT4] [FT8] | 10 |

(Headers aligned to the left)

### After:
| My Callsign | 17M | 20M | 30M | 40M | Total |
|-------------|-----|-----|-----|-----|-------|
| R3LO | [CW] [FT8] | [FT4] [FT8] | [FT8] | [FT4] [FT8] | 10 |

(Headers centered)

## Note

The data in the table body (`<td>`) remains left-aligned for better readability.

## Files Updated

1. `QRZ_COM_FORM_FOR_USER.md` - Form for QRZ.com
2. `test_qrz_user_en.html` - Test page

## Testing

Open test page:
```
http://127.0.0.1:8080/test_qrz_user_en.html
```

Search for any callsign and verify that:
- Column headers are centered
- Data in cells remains left-aligned
