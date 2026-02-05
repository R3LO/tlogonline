// Achievements page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const filterMyCallsign = document.getElementById('filter_my_callsign');
    const filterBand = document.getElementById('filter_band');
    const filterMode = document.getElementById('filter_mode');
    const filterPropMode = document.getElementById('filter_prop_mode');
    const filterSatName = document.getElementById('filter_sat_name');
    const applyBtn = document.getElementById('apply_filters');
    const resetBtn = document.getElementById('reset_filters');
    const filteredStats = document.getElementById('filtered_stats');
    const filteredMessage = document.getElementById('filtered_message');
    const closeFilteredStats = document.getElementById('close_filtered_stats');

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Apply filters
    function applyFilters() {
        const filters = {
            my_callsign: filterMyCallsign.value.trim().toUpperCase(),
            band: filterBand.value,
            mode: filterMode.value,
            prop_mode: filterPropMode.value,
            sat_name: filterSatName.value
        };

        applyBtn.disabled = true;
        applyBtn.innerHTML = '<span>⏳</span> Загрузка...';

        fetch('/achievements/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filters),
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            applyBtn.disabled = false;
            applyBtn.innerHTML = '<span>🔍</span> Применить';

            if (data.success) {
                updateStats(data);
                filteredStats.style.display = 'block';
                filteredMessage.textContent = data.message;
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            applyBtn.disabled = false;
            applyBtn.innerHTML = '<span>🔍</span> Применить';
            alert('Ошибка при применении фильтров: ' + error.message);
        });
    }

    // Update stats
    function updateStats(data) {
        const totalElements = document.querySelectorAll('.stats-card .stats-number');
        if (totalElements.length > 0) totalElements[0].textContent = data.total_qso;
        if (totalElements.length > 1) totalElements[1].textContent = data.unique_callsigns;
        if (totalElements.length > 2) totalElements[2].textContent = data.dxcc_count || 0;
        if (totalElements.length > 3) totalElements[3].textContent = data.r150s_count;
        if (totalElements.length > 4) totalElements[4].textContent = data.state_count || 0;

        const statQso = document.getElementById('stat_qso');
        if (statQso) statQso.textContent = data.total_qso;

        const statUniq = document.getElementById('stat_uniq_callsigns');
        if (statUniq) statUniq.textContent = data.unique_callsigns;

        const statDxcc = document.getElementById('stat_dxcc');
        if (statDxcc) statDxcc.textContent = data.dxcc_count || 0;

        const statR150s = document.getElementById('stat_r150s');
        if (statR150s) statR150s.textContent = data.r150s_count;

        const statState = document.getElementById('stat_state');
        if (statState) statState.textContent = data.state_count || 0;

        const statCqz = document.getElementById('stat_cqz');
        if (statCqz) statCqz.textContent = data.cqz_count || 0;

        const statItuz = document.getElementById('stat_ituz');
        if (statItuz) statItuz.textContent = data.ituz_count || 0;

        const statGrid = document.getElementById('stat_grid');
        if (statGrid) statGrid.textContent = data.grids_count || 0;

        // Update bands
        const bandSection = document.querySelectorAll('.col-md-6:first-child div:not(.section-title)');
        if (bandSection.length > 0) {
            let bandsHtml = '';
            for (const [band, count] of Object.entries(data.bands || {})) {
                bandsHtml += `<span class="band-badge">${band} (${count})</span>`;
            }
            bandSection[0].innerHTML = bandsHtml || '<p class="text-muted">Нет данных</p>';
        }

        // Update modes
        const modeSection = document.querySelectorAll('.col-md-6:last-child div:not(.section-title)');
        if (modeSection.length > 0) {
            let modesHtml = '';
            for (const [mode, count] of Object.entries(data.modes || {})) {
                modesHtml += `<span class="mode-badge">${mode} (${count})</span>`;
            }
            modeSection[0].innerHTML = modesHtml || '<p class="text-muted">Нет данных</p>';
        }

        // Update achievements
        const achievementsContainer = document.querySelector('.row:not(.mb-4):has(.achievement-card)');
        if (achievementsContainer && data.achievements_html) {
            achievementsContainer.innerHTML = data.achievements_html;
        }
    }

    // Reset filters
    function resetFilters() {
        filterMyCallsign.value = '';
        filterBand.value = '';
        filterMode.value = '';
        filterPropMode.value = '';
        filterSatName.value = '';
        filteredStats.style.display = 'none';
        window.location.href = '/achievements/';
    }

    // Event listeners
    applyBtn.addEventListener('click', applyFilters);
    resetBtn.addEventListener('click', resetFilters);
    closeFilteredStats.addEventListener('click', function() {
        filteredStats.style.display = 'none';
        resetFilters();
    });
});