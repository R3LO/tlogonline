/* =====================================
   QO-100 JavaScript функциональность
   ===================================== */

// Инициализация QO-100 функциональности при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initQO100();
});

/**
 * Основная инициализация QO-100 функциональности
 */
function initQO100() {
    initConverter();
    initUploader();
    initFilters();
    initSatelliteTracking();
}

/**
 * Инициализация конвертера ADIF файлов
 */
function initConverter() {
    const uploadForm = document.getElementById('adif-upload-form');
    const convertButton = document.getElementById('convert-adif-btn');
    
    if (uploadForm && convertButton) {
        uploadForm.addEventListener('submit', handleADIFConversion);
        convertButton.addEventListener('click', handleADIFConversion);
    }
    
    // Предварительный просмотр файла
    const fileInput = document.getElementById('adif-file');
    if (fileInput) {
        fileInput.addEventListener('change', previewADIFFile);
    }
}

/**
 * Предварительный просмотр ADIF файла
 */
function previewADIFFile(event) {
    const file = event.target.files[0];
    const previewDiv = document.getElementById('adif-preview');
    
    if (!file || !previewDiv) return;
    
    // Проверяем тип файла
    if (!file.name.toLowerCase().endsWith('.adi') && !file.name.toLowerCase().endsWith('.adif')) {
        showNotification('Пожалуйста, выберите ADIF файл (.adi или .adif)', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const content = e.target.result;
            const stats = parseADIFStats(content);
            
            previewDiv.innerHTML = `
                <div class="adif-preview-stats">
                    <h6><span>📊</span> Статистика файла:</h6>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="stat-item">
                                <strong>QSO записей:</strong> ${stats.qsoCount}
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-item">
                                <strong>Спутники:</strong> ${stats.satellites.join(', ') || 'Не указано'}
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-item">
                                <strong>Диапазоны:</strong> ${stats.bands.join(', ') || 'Не указано'}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            previewDiv.style.display = 'block';
            
        } catch (error) {
            console.error('Ошибка парсинга ADIF:', error);
            showNotification('Ошибка при анализе файла', 'error');
        }
    };
    
    reader.readAsText(file);
}

/**
 * Парсинг статистики из ADIF файла
 */
function parseADIFStats(content) {
    const qsoMatches = content.match(/<QSO_DATE:8>\d{8}/g) || [];
    const satMatches = content.match(/<SAT_NAME:[^>]*>[^<]*/g) || [];
    const bandMatches = content.match(/<BAND:[^>]*>[^<]*/g) || [];
    
    const satellites = [...new Set(satMatches.map(match => {
        const value = match.match(/>([^<]*)/);
        return value ? value[1] : '';
    }))].filter(Boolean);
    
    const bands = [...new Set(bandMatches.map(match => {
        const value = match.match(/>([^<]*)/);
        return value ? value[1] : '';
    }))].filter(Boolean);
    
    return {
        qsoCount: qsoMatches.length,
        satellites: satellites,
        bands: bands
    };
}

/**
 * Обработка конвертации ADIF файла
 */
function handleADIFConversion(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('adif-file');
    const formData = new FormData();
    
    if (!fileInput.files[0]) {
        showNotification('Пожалуйста, выберите файл для конвертации', 'error');
        return;
    }
    
    formData.append('adif_file', fileInput.files[0]);
    
    const convertButton = document.getElementById('convert-adif-btn');
    const originalText = convertButton.innerHTML;
    
    // Показываем состояние загрузки
    convertButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Конвертация...';
    convertButton.disabled = true;
    
    fetch('/qso100/convert/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Конвертация завершена успешно!', 'success');
            
            // Показываем результаты
            showConversionResults(data);
        } else {
            showNotification('Ошибка при конвертации: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка конвертации:', error);
        showNotification('Произошла ошибка при конвертации', 'error');
    })
    .finally(() => {
        convertButton.innerHTML = originalText;
        convertButton.disabled = false;
    });
}

/**
 * Показ результатов конвертации
 */
function showConversionResults(data) {
    const resultsDiv = document.getElementById('conversion-results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="conversion-results">
            <h6><span>✅</span> Результаты конвертации:</h6>
            <div class="alert alert-success">
                <strong>Обработано QSO:</strong> ${data.processed_qso}<br>
                <strong>Добавлено в базу:</strong> ${data.added_qso}<br>
                <strong>Пропущено (дубликаты):</strong> ${data.skipped_qso}
            </div>
            
            ${data.download_url ? `
                <a href="${data.download_url}" class="btn btn-primary" download>
                    <span>📥</span> Скачать отчет
                </a>
            ` : ''}
        </div>
    `;
    
    resultsDiv.style.display = 'block';
}

/**
 * Инициализация загрузчика файлов
 */
function initUploader() {
    const dropZone = document.getElementById('adif-drop-zone');
    const fileInput = document.getElementById('adif-file');
    
    if (dropZone && fileInput) {
        // Drag & Drop функциональность
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('drop', handleFileDrop);
        dropZone.addEventListener('dragleave', handleDragLeave);
        
        // Клик по зоне загрузки
        dropZone.addEventListener('click', () => fileInput.click());
    }
}

/**
 * Обработка перетаскивания файлов
 */
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

function handleFileDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        previewADIFFile({ target: { files: files } });
    }
}

/**
 * Инициализация фильтров
 */
function initFilters() {
    const filterInputs = document.querySelectorAll('.qo100-filter');
    
    filterInputs.forEach(input => {
        input.addEventListener('change', applyFilters);
        input.addEventListener('input', debounce(applyFilters, 300));
    });
}

/**
 * Применение фильтров
 */
function applyFilters() {
    const filters = {};
    
    document.querySelectorAll('.qo100-filter').forEach(input => {
        if (input.value.trim()) {
            filters[input.name] = input.value.trim();
        }
    });
    
    fetch('/qso100/filter/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        updateQSOList(data.qso_list);
    })
    .catch(error => {
        console.error('Ошибка фильтрации:', error);
    });
}

/**
 * Обновление списка QSO
 */
function updateQSOList(qsoList) {
    const tableBody = document.querySelector('#qo100-qso-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    qsoList.forEach(qso => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${qso.qso_date}</td>
            <td>${qso.time_on}</td>
            <td>${qso.callsign}</td>
            <td>${qso.mode}</td>
            <td>${qso.band}</td>
            <td>${qso.sat_name || 'Не указан'}</td>
            <td>${qso.rst_sent}/${qso.rst_rcvd}</td>
        `;
        tableBody.appendChild(row);
    });
}

/**
 * Инициализация отслеживания спутника
 */
function initSatelliteTracking() {
    const trackingDiv = document.getElementById('satellite-tracking');
    if (!trackingDiv) return;
    
    // Получаем текущую информацию о спутнике
    fetch('/api/satellite/current/')
    .then(response => response.json())
    .then(data => {
        updateSatelliteInfo(data);
    })
    .catch(error => {
        console.error('Ошибка получения данных спутника:', error);
    });
    
    // Обновляем данные каждые 30 секунд
    setInterval(updateSatelliteTracking, 30000);
}

/**
 * Обновление информации о спутнике
 */
function updateSatelliteInfo(data) {
    const trackingDiv = document.getElementById('satellite-tracking');
    if (!trackingDiv) return;
    
    trackingDiv.innerHTML = `
        <div class="satellite-info">
            <h6><span>🛰️</span> QO-100 Текущее состояние</h6>
            <div class="row">
                <div class="col-md-6">
                    <div class="satellite-status">
                        <strong>Орбитальная позиция:</strong> ${data.position}<br>
                        <strong>Доплер сдвиг:</strong> ${data.doppler_shift} Hz<br>
                        <strong>Время до следующего прохода:</strong> ${data.next_pass}
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="satellite-status">
                        <strong>Статус:</strong> 
                        <span class="badge ${data.active ? 'bg-success' : 'bg-warning'}">
                            ${data.active ? 'Активен' : 'Неактивен'}
                        </span><br>
                        <strong>Солнечная батарея:</strong> ${data.solar_power}%<br>
                        <strong>Температура:</strong> ${data.temperature}°C
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Утилита для debounce
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Утилита для получения CSRF токена
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

/**
 * Показ уведомлений
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}