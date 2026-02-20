# CSS Alignment Fix

## Problem

The CSS rule:
```css
#tlog-result-table th,
#tlog-result-table td {
    text-align: left;
}
```

Was overriding the `text-align: center` for table headers due to CSS specificity and order.

## Solution

Separated the CSS rules:

**Before:**
```css
#tlog-result-table th,
#tlog-result-table td {
    padding: 10px;
    text-align: left;  /* Applied to both th and td */
    border-bottom: 1px solid #ddd;
    border-right: 1px solid #ddd;
}
#tlog-result-table th {
    text-align: center;  /* Overridden by the rule above */
}
```

**After:**
```css
#tlog-result-table th,
#tlog-result-table td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
    border-right: 1px solid #ddd;
}
#tlog-result-table th {
    background: #0066cc;
    color: white;
    font-weight: bold;
    text-align: center;  /* Centered for headers */
}
#tlog-result-table td {
    text-align: left;  /* Left aligned for data cells */
}
```

## Result

- ✅ Table headers (`th`) are centered
- ✅ Table data cells (`td`) are left-aligned
- ✅ No CSS conflicts

## Files Updated

1. `QRZ_COM_FORM_FOR_USER.md` - Form for QRZ.com
2. `test_qrz_user_en.html` - Test page
