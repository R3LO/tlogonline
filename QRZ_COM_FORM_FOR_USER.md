# QSO Search Form for QRZ.com (for specific user)

This file contains the QSO search form code for embedding on a specific user's page on QRZ.com.

## How it works:

1. **Hidden field `owner_callsign`**: contains the page owner's callsign (e.g., "R3LO")
2. **Visible input field**: user enters THEIR callsign (who they worked with)
3. **API**:
   - Finds user_id by `owner_callsign` in RadioProfile
   - Searches QSO where `user_id` = found AND `callsign` = entered callsign

## Installation instructions:

### Step 1: Change owner callsign

Find this line in the code below:
```javascript
const OWNER_CALLSIGN = 'R3LO';  // REPLACE WITH YOUR CALLSIGN
```

And replace `'R3LO'` with your callsign.

### Step 2: Change server URL (if needed)

Find this line:
```javascript
const API_BASE_URL = 'https://tlogonline.com';  // Change to your URL
```

### Step 3: Copy and paste to QRZ.com

Copy all the code below and paste it into the "Bio" field of your QRZ.com profile.

## Form code:

```html
<!-- TlogOnline QSO Search Form -->
<div id="tlog-search-container" style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto;">
    <style>
        #tlog-search-container {
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
        }
        #tlog-search-form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        #tlog-callsign-input {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }
        #tlog-search-btn {
            padding: 10px 20px;
            background: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        #tlog-search-btn:hover {
            background: #0052a3;
        }
        #tlog-search-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        #tlog-result {
            margin-top: 20px;
        }
        #tlog-result-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 4px;
            overflow: hidden;
        }
        #tlog-result-table th,
        #tlog-result-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            border-right: 1px solid #ddd;
        }
        #tlog-result-table th:last-child,
        #tlog-result-table td:last-child {
            border-right: none;
        }
        #tlog-result-table th {
            background: #0066cc;
            color: white;
            font-weight: bold;
        }
        #tlog-result-table tr:hover {
            background: #f9f9f9;
        }
        .mode-badge {
            display: inline-block;
            padding: 3px 8px;
            margin: 2px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            background: #007bff;
            color: white;
        }
        .mode-badge.CW { background: #28a745; }
        .mode-badge.SSB { background: #17a2b8; }
        .mode-badge.FT8 { background: #ffc107; color: #333; }
        .mode-badge.FT4 { background: #fd7e14; }
        .mode-badge.AM { background: #6c757d; }
        .mode-badge.FM { background: #6c757d; }
        .mode-badge.PSK31 { background: #6f42c1; }
        .mode-badge.RTTY { background: #6f42c1; }
        .mode-badge.JT65 { background: #e83e8c; }
        .mode-badge.SSTV { background: #e83e8c; }
        .mode-badge.DIGITAL { background: #6610f2; }
        #tlog-loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        #tlog-error {
            background: #ffe6e6;
            color: #cc0000;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        #tlog-not-found {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
            margin-top: 10px;
            font-weight: bold;
        }
        .tlog-title {
            color: #0066cc;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
    </style>

    <div class="tlog-title">📻 Check QSO in my log</div>

    <form id="tlog-search-form">
        <input
            type="text"
            id="tlog-callsign-input"
            placeholder="Enter your callsign"
            maxlength="20"
        />
        <button type="submit" id="tlog-search-btn">Search</button>
    </form>

    <div id="tlog-result"></div>
</div>

<script>
(function() {
    // ==================== CONFIGURATION ====================
    // REPLACE WITH YOUR CALLSIGN
    const OWNER_CALLSIGN = 'R3LO';

    // REPLACE WITH YOUR SERVER URL
    const API_BASE_URL = 'https://tlogonline.com';
    // =====================================================

    const form = document.getElementById('tlog-search-form');
    const input = document.getElementById('tlog-callsign-input');
    const button = document.getElementById('tlog-search-btn');
    const resultDiv = document.getElementById('tlog-result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const searchCallsign = input.value.trim().toUpperCase();

        if (!searchCallsign) {
            showError('Please enter your callsign');
            return;
        }

        showLoading();
        button.disabled = true;

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/v1/public/qso-search/?owner_callsign=${encodeURIComponent(OWNER_CALLSIGN)}&search_callsign=${encodeURIComponent(searchCallsign)}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Search error:', error);
            showError(`Search error: ${error.message}. Please check your connection.`);
        } finally {
            button.disabled = false;
        }
    });

    function showLoading() {
        resultDiv.innerHTML = '<div id="tlog-loading">⏳ Searching...</div>';
    }

    function showError(message) {
        resultDiv.innerHTML = `<div id="tlog-error">❌ ${message}</div>`;
    }

    function displayResults(data) {
        if (!data.found) {
            const message = data.message || 'Not found';
            resultDiv.innerHTML = `
                <div id="tlog-not-found">
                    📭 No QSO found for callsign <strong>${data.search_callsign || ''}</strong> in log of <strong>${data.owner_callsign || ''}</strong>
                </div>
            `;
            return;
        }

        if (!data.results || data.results.length === 0) {
            resultDiv.innerHTML = `
                <div id="tlog-not-found">
                    📭 No QSO found for callsign <strong>${data.search_callsign}</strong> in log of <strong>${data.owner_callsign}</strong>
                </div>
            `;
            return;
        }

        // Collect all unique bands/satellites
        const allBands = new Set();
        data.results.forEach(result => {
            Object.keys(result.bands).forEach(band => allBands.add(band));
        });

        // Sort bands: numeric first, then SAT, then others
        const sortedBands = Array.from(allBands).sort((a, b) => {
            // SAT bands go last
            if (a.startsWith('SAT:') && !b.startsWith('SAT:')) return 1;
            if (!a.startsWith('SAT:') && b.startsWith('SAT:')) return -1;

            // Extract numeric value for regular bands
            const aNum = parseInt(a.replace('m', ''));
            const bNum = parseInt(b.replace('m', ''));

            if (!isNaN(aNum) && !isNaN(bNum)) {
                return aNum - bNum; // Ascending for bands
            }

            // For SAT, sort by satellite name
            if (a.startsWith('SAT:') && b.startsWith('SAT:')) {
                return a.localeCompare(b);
            }

            // Fallback to alphabetical
            return a.localeCompare(b);
        });

        // Create table
        let html = `
            <table id="tlog-result-table">
                <thead>
                    <tr>
                        <th>My Callsign</th>
                        ${sortedBands.map(band => {
                            if (band.startsWith('SAT:')) {
                                const satName = band.replace('SAT:', '');
                                return `<th>SAT<br><small>${satName}</small></th>`;
                            }
                            return `<th>${band}</th>`;
                        }).join('')}
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.results.forEach(result => {
            const totalQSO = Object.values(result.bands).reduce(
                (sum, modes) => sum + Object.values(modes).reduce((a, b) => a + b, 0),
                0
            );

            html += `<tr><td><strong>${result.my_callsign}</strong></td>`;

            sortedBands.forEach(band => {
                const modes = result.bands[band];
                if (modes && Object.keys(modes).length > 0) {
                    // Sort modes alphabetically and create badges
                    const sortedModes = Object.keys(modes).sort();
                    const modeBadges = sortedModes.map(mode => {
                        const modeClass = mode.replace(/[^a-zA-Z0-9]/g, '');
                        return `<span class="mode-badge ${modeClass}">${mode}</span>`;
                    }).join(' ');
                    html += `<td>${modeBadges}</td>`;
                } else {
                    html += '<td>-</td>';
                }
            });

            html += `<td><strong>${totalQSO}</strong></td></tr>`;
        });

        html += `
                </tbody>
            </table>
            <p style="margin-top: 10px; font-size: 12px; color: #666; text-align: center;">
                ✅ QSO found for callsign <strong>${data.search_callsign}</strong> in log of <strong>${data.owner_callsign}</strong>
            </p>
        `;

        resultDiv.innerHTML = html;
    }

    // Auto-focus on input field on load
    window.addEventListener('load', function() {
        input.focus();
    });

    // Handle Enter key - use keydown for better compatibility
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    });
})();
</script>
<!-- End TlogOnline QSO Search Form -->
```

## API Example

**Request:**
```
GET https://tlogonline.com/api/v1/public/qso-search/?owner_callsign=R3LO&search_callsign=UA1AAA
```

**Response (if found):**
```json
{
    "found": true,
    "owner_callsign": "R3LO",
    "search_callsign": "UA1AAA",
    "results": [
        {
            "my_callsign": "R3LO",
            "modes": {
                "SSB": 5,
                "CW": 3,
                "FT8": 10
            }
        },
        {
            "my_callsign": "R3LO/P",
            "modes": {
                "SSB": 2
            }
        }
    ]
}
```

**Response (if not found):**
```json
{
    "found": false,
    "owner_callsign": "R3LO",
    "search_callsign": "UA1XXX",
    "message": "Not found"
}
```

## Testing

1. Open test page: `http://127.0.0.1:8080/test_qrz_user.html`
2. Enter owner_callsign (e.g., "R3LO")
3. Enter search_callsign (e.g., "GJ0KYZ")
4. Click "Search"
5. Check the result

## Features

- ✅ owner_callsign is used to get user_id from RadioProfile
- ✅ Shows only QSO for a specific user
- ✅ Rows = my_callsign (all owner's callsigns)
- ✅ Columns = mode types
- ✅ Works on external sites (CORS configured)
