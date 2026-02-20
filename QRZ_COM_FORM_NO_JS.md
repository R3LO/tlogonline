# QSO Search Form for QRZ.com (No JavaScript)

This form works WITHOUT JavaScript - perfect for QRZ.com which blocks scripts.

## How to use

1. **Change the owner callsign** (find `R3LO` and replace with your callsign)
2. **Copy the HTML code below**
3. **Paste it into your QRZ.com profile** in the "Bio" field

## Form Code

```html
<!-- TlogOnline QSO Search Form (No JavaScript) -->
<div style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; background: #f5f5f5; border: 1px solid #ddd; border-radius: 8px; padding: 20px;">
    <div style="color: #0066cc; margin-bottom: 15px; font-size: 18px; font-weight: bold; text-align: center;">
        Check QSO in my log
    </div>

    <form action="https://tlogonline.com/public/qso-search/" method="get" target="_blank" style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
        <!-- Hidden owner_callsign field - CHANGE THIS TO YOUR CALLSIGN -->
        <input type="hidden" name="owner_callsign" value="R3LO">

        <input
            type="text"
            name="search_callsign"
            placeholder="Enter your callsign"
            maxlength="20"
            style="flex: 1; min-width: 200px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;"
        />

        <button
            type="submit"
            style="padding: 10px 20px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold;"
        >
            Search
        </button>
    </form>

    <div style="font-size: 12px; color: #666; text-align: center;">
        Enter your callsign and click Search to see QSOs in my log
    </div>
</div>
<!-- End TlogOnline QSO Search Form -->
```

## How it works

1. User enters their callsign in the input field
2. User clicks "Search" button
3. Form submits GET request to: `https://tlogonline.com/public/qso-search/?owner_callsign=R3LO&search_callsign=UA1AAA`
4. Server returns HTML page with results in a new tab/window
5. Results show bands as columns and modes as colored badges

## Configuration

### Change owner callsign

Find this line in the form:
```html
<input type="hidden" name="owner_callsign" value="R3LO">
```

Replace `R3LO` with your callsign.

### Change server URL

If your server has a different URL, change:
```html
<form action="https://tlogonline.com/public/qso-search/" method="get">
```

## Features

- ✅ NO JavaScript required
- ✅ Works on QRZ.com
- ✅ Simple HTML form
- ✅ Results open in new tab/window
- ✅ Color-coded mode badges
- ✅ Bands as columns
- ✅ Satellite support (shows SAT:Name)

## Testing

You can test locally:
```html
<form action="http://localhost:8000/public/qso-search/" method="get">
```

## Notes

- This form uses a standard HTML GET request
- Results will open in the same tab/window (you can add `target="_blank"` to the form tag to open in new tab)
- No AJAX or JavaScript - works on any site that allows HTML forms
