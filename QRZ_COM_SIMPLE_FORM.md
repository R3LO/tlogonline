# Simple QSO Search Form for QRZ.com

## Minimal form that complies with QRZ.com rules

### Rules check:
- ✅ No JavaScript
- ✅ No HTML event attributes (onclick, onmouseover, etc.)
- ✅ No iframe
- ✅ No external images
- ✅ No QR codes
- ✅ No auto-playing sounds
- ✅ Family-friendly content

### Form code:

```html
<form action="https://tlogonline.com/public/qso-search/" method="get" target="_blank">
    <input type="hidden" name="owner_callsign" value="R3LO">
    Check QSO in my log:
    <input type="text" name="search_callsign" placeholder="Enter your callsign" maxlength="20">
    <input type="submit" value="Search">
</form>
```

### Instructions:

1. Replace `R3LO` with your callsign
2. Replace `https://tlogonline.com` with your server URL if different
3. Copy and paste into QRZ.com Bio field

### Why this works:

- Minimal HTML - less likely to be filtered
- No inline styles - some sites filter style attributes
- Standard form tags - universally accepted
- No event attributes - QRZ.com prohibits onclick, etc.

### Alternative (if form above doesn't work):

```html
<p>Check QSO in my log: 
<a href="https://tlogonline.com/public/qso-search/?owner_callsign=R3LO&search_callsign=YOUR_CALLSIGN" target="_blank">Click here</a>
</p>
```

User replaces YOUR_CALLSIGN with their callsign in the URL.
