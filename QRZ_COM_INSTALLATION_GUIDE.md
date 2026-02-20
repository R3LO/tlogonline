# QRZ.com Installation Guide

## What to put on QRZ.com

Use the HTML form from `QRZ_COM_FORM_NO_JS.md`

## How it works

1. User enters their callsign on your QRZ.com page
2. User clicks "Search" button
3. **Results open in a NEW TAB/WINDOW** (not iframe)
4. Results are displayed on your tlogonline.com server

## Step-by-Step Installation

### 1. Open `QRZ_COM_FORM_NO_JS.md`

Copy the HTML code from this file.

### 2. Change the owner callsign

Find this line:
```html
<input type="hidden" name="owner_callsign" value="R3LO">
```

Replace `R3LO` with your callsign.

### 3. Change the server URL (if needed)

If your server has a different URL:
```html
<form action="https://tlogonline.com/public/qso-search/" method="get" target="_blank">
```

### 4. Copy and paste to QRZ.com

1. Go to your QRZ.com profile
2. Click "Edit Bio" or "Edit Profile"
3. Paste the HTML code into the "Bio" field
4. Save

## Why NOT use iframe?

QRZ.com and most sites block iframes from external domains for security reasons (X-Frame-Options, CSP).

Using `target="_blank"` is the correct approach because:
- ✅ Works on all sites
- ✅ No security restrictions
- ✅ User can see full results
- ✅ Easy to implement

## User Experience

1. Visitor lands on your QRZ.com page
2. Sees the form: "Check QSO in my log"
3. Enters their callsign (e.g., "UA1AAA")
4. Clicks "Search"
5. **New tab opens** with results
6. Results show table with bands and modes
7. User can close the tab and return to QRZ.com

## Testing

Before putting on QRZ.com, test locally:

1. Change the form action:
   ```html
   <form action="http://127.0.0.1:8000/public/qso-search/" method="get" target="_blank">
   ```

2. Create a test HTML file with the form
3. Open in browser and test

## Notes

- Form uses `target="_blank"` to open results in new tab
- No JavaScript required
- Works on QRZ.com and any site that allows HTML
- Results are hosted on your tlogonline.com server
- Users can bookmark the results page
