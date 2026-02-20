# Enter Key and Table Borders Updates

## Changes Made

### 1. **Enter Key Handling**

**Problem:** Form was submitting via default browser behavior when Enter was pressed, causing page reload or unexpected behavior.

**Solution:** Added `e.preventDefault()` to prevent default form submission and manually trigger the search via JavaScript.

**Code:**
```javascript
// Handle Enter key - prevent default form submission
input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        // Manually trigger the form submit handler
        form.dispatchEvent(new Event('submit'));
    }
});
```

**Note:** Using `keydown` instead of `keypress` for better browser compatibility (keypress is deprecated).

### 2. **Table Column Borders**

**Problem:** No visual separation between columns in the results table.

**Solution:** Added vertical borders between columns using CSS.

**CSS:**
```css
#tlog-result-table th,
#tlog-result-table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #ddd;
    border-right: 1px solid #ddd;  /* New: vertical border */
}

#tlog-result-table th:last-child,
#tlog-result-table td:last-child {
    border-right: none;  /* Remove border from last column */
}
```

## Table Appearance

### Before:
| My Callsign | 17M | 20M | 30M | 40M | Total |
|-------------|-----|-----|-----|-----|-------|
| R3LO | [CW] [FT8] | [FT4] [FT8] | [FT8] | [FT4] [FT8] | 10 |

### After:
| My Callsign | 17M | 20M | 30M | 40M | Total |
|-------------|-----|-----|-----|-----|-------|
| R3LO | [CW] [FT8] | [FT4] [FT8] | [FT8] | [FT4] [FT8] | 10 |

(Vertical lines between columns)

## Behavior

### Enter Key:
- ✅ Pressing Enter triggers search
- ✅ No page reload
- ✅ No default form submission
- ✅ Works consistently across browsers

### Table Borders:
- ✅ Vertical lines between columns
- ✅ No border on the last column
- ✅ Same style as horizontal borders (light gray)

## Files Updated

1. `QRZ_COM_FORM_FOR_USER.md` - Form for QRZ.com
2. `test_qrz_user_en.html` - Test page

## Testing

1. Open test page: `http://127.0.0.1:8080/test_qrz_user_en.html`
2. Enter callsign in the input field
3. Press Enter - search should trigger without page reload
4. Check that table has vertical borders between columns

## Browser Compatibility

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

Using `keydown` event instead of deprecated `keypress` ensures compatibility with all modern browsers.
