// ========== Функции для добавления QSO ==========

// Функция для получения CSRF токена
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

// Функция для показа уведомлений
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Функции для работы с cookies
function setCookie(name, value, days) {
    let expires = '';
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + (encodeURIComponent(value) || '') + expires + '; path=/';
}

// getCookie и showAlert определены в logbook.js и доступны глобально

// Загрузка настроек из cookies при открытии модального окна
function initAddQSOModal() {
    document.getElementById('addQSOModal').addEventListener('show.bs.modal', function() {
        // Устанавливаем текущую дату и время
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0];
        const timeStr = now.toTimeString().slice(0, 5);

        // Только если поля пустые, устанавливаем текущие дату и время
        if (!document.getElementById('add_date').value) {
            document.getElementById('add_date').value = dateStr;
        }
        if (!document.getElementById('add_time').value) {
            document.getElementById('add_time').value = timeStr;
        }

        // Загружаем сохраненные настройки из cookies
        const savedSatQSO = getCookie('add_qso_sat_qso');
        const savedSatPropMode = getCookie('add_qso_sat_prop_mode');
        const savedSatName = getCookie('add_qso_sat_name');
        const savedBand = getCookie('add_qso_band');
        const savedMode = getCookie('add_qso_mode');
        const savedLotw = getCookie('add_qso_lotw');
        const savedMyCallsign = getCookie('add_qso_my_callsign');

        // Показываем/скрываем поля SAT в зависимости от чекбокса
        const satFields = document.getElementById('sat_fields');
        const satPlaceholder = document.getElementById('sat_fields_placeholder');
        
        if (savedSatQSO === 'true') {
            document.getElementById('add_sat_qso').checked = true;
            satFields.style.display = 'block';
            satPlaceholder.style.display = 'none';
        } else {
            document.getElementById('add_sat_qso').checked = false;
            satFields.style.display = 'none';
            satPlaceholder.style.display = 'flex';
            // Очищаем SAT поля если Sat QSO не отмечен
            document.getElementById('add_sat_prop_mode').value = '';
            document.getElementById('add_sat_name').value = '';
        }

        if (savedSatPropMode && savedSatQSO === 'true') document.getElementById('add_sat_prop_mode').value = savedSatPropMode;
        if (savedSatName && savedSatQSO === 'true') document.getElementById('add_sat_name').value = savedSatName;
        if (savedBand) document.getElementById('add_band').value = savedBand;
        if (savedMode) document.getElementById('add_mode').value = savedMode;
        if (savedMyCallsign) document.getElementById('add_my_callsign').value = savedMyCallsign;

        // Добавляем обработчики для автоматического преобразования в верхний регистр
        const textFields = ['add_my_callsign', 'add_callsign', 'add_band', 'add_mode',
                           'add_rst_rcvd', 'add_rst_sent', 'add_my_gridsquare',
                           'add_gridsquare', 'add_sat_prop_mode', 'add_sat_name'];
        textFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', function() {
                    this.value = this.value.toUpperCase();
                });
            }
        });
    });
}

// Показ/скрытие полей спутниковой связи
function initSatQSOCheckbox() {
    document.getElementById('add_sat_qso').addEventListener('change', function() {
        const satFields = document.getElementById('sat_fields');
        const satPlaceholder = document.getElementById('sat_fields_placeholder');
        
        if (this.checked) {
            satFields.style.display = 'block';
            satPlaceholder.style.display = 'none';
        } else {
            satFields.style.display = 'none';
            satPlaceholder.style.display = 'flex';
            // Очищаем поля при выключении
            document.getElementById('add_sat_prop_mode').value = '';
            document.getElementById('add_sat_name').value = '';
        }
    });
}

// Сохранение настроек в cookies при отправке формы
function saveQSOsettings() {
    setCookie('add_qso_sat_qso', document.getElementById('add_sat_qso').checked, 365);

    // Сохраняем SAT настройки только если Sat QSO включен
    if (document.getElementById('add_sat_qso').checked) {
        setCookie('add_qso_sat_prop_mode', document.getElementById('add_sat_prop_mode').value, 365);
        setCookie('add_qso_sat_name', document.getElementById('add_sat_name').value, 365);
    } else {
        // Если Sat QSO не включен, очищаем SAT настройки
        setCookie('add_qso_sat_prop_mode', '', 365);
        setCookie('add_qso_sat_name', '', 365);
    }

    setCookie('add_qso_band', document.getElementById('add_band').value, 365);
    setCookie('add_qso_mode', document.getElementById('add_mode').value, 365);
    setCookie('add_qso_my_callsign', document.getElementById('add_my_callsign').value, 365);
}

// Сброс формы
function resetAddQSOForm() {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toTimeString().slice(0, 5);

    document.getElementById('add_date').value = dateStr;
    document.getElementById('add_time').value = timeStr;
    document.getElementById('add_callsign').value = '';
    document.getElementById('add_frequency').value = '';
    document.getElementById('add_rst_rcvd').value = '';
    document.getElementById('add_rst_sent').value = '';
    document.getElementById('add_gridsquare').value = '';
    document.getElementById('add_cqz').value = '';
    document.getElementById('add_ituz').value = '';

    // Сбрасываем чекбокс Sat QSO но оставляем сохраненные настройки
    const satQSO = getCookie('add_qso_sat_qso') === 'true';
    const satFields = document.getElementById('sat_fields');
    const satPlaceholder = document.getElementById('sat_fields_placeholder');
    
    document.getElementById('add_sat_qso').checked = satQSO;
    
    if (satQSO) {
        satFields.style.display = 'block';
        satPlaceholder.style.display = 'none';
    } else {
        satFields.style.display = 'none';
        satPlaceholder.style.display = 'flex';
    }

    // Очищаем SAT поля
    if (satQSO) {
        const savedSatPropMode = getCookie('add_qso_sat_prop_mode');
        const savedSatName = getCookie('add_qso_sat_name');
        document.getElementById('add_sat_prop_mode').value = savedSatPropMode || '';
        document.getElementById('add_sat_name').value = savedSatName || '';
    } else {
        document.getElementById('add_sat_prop_mode').value = '';
        document.getElementById('add_sat_name').value = '';
    }
}

// Добавление QSO
function initSaveAddQSO() {
    document.getElementById('saveAddQSO').addEventListener('click', function() {
        // Проверяем обязательные поля
        const date = document.getElementById('add_date').value;
        const time = document.getElementById('add_time').value;
        const callsign = document.getElementById('add_callsign').value.trim();

        if (!date || !time || !callsign) {
            showAlert('danger', 'Заполните обязательные поля: дата, время, позывной');
            return;
        }

        this.disabled = true;
        this.innerHTML = '<span>⏳</span> Сохранение...';

        // Проверяем, включен ли Sat QSO
        const satQSO = document.getElementById('add_sat_qso').checked;

        // Собираем данные формы вручную
        const data = {
            date: date,
            time: time,
            my_callsign: document.getElementById('add_my_callsign').value.trim().toUpperCase(),
            callsign: callsign.toUpperCase(),
            band: document.getElementById('add_band').value.trim().toUpperCase() || null,
            mode: document.getElementById('add_mode').value.trim().toUpperCase(),
            frequency: document.getElementById('add_frequency').value,
            rst_rcvd: document.getElementById('add_rst_rcvd').value.toUpperCase(),
            rst_sent: document.getElementById('add_rst_sent').value.toUpperCase(),
            my_gridsquare: document.getElementById('add_my_gridsquare').value.toUpperCase(),
            gridsquare: document.getElementById('add_gridsquare').value.toUpperCase(),
            cqz: document.getElementById('add_cqz').value,
            ituz: document.getElementById('add_ituz').value,
            lotw: 'N',
            sat_qso: satQSO ? 'Y' : 'N'
        };

        // Добавляем SAT поля только если Sat QSO включен
        if (satQSO) {
            data.prop_mode = document.getElementById('add_sat_prop_mode').value.toUpperCase();
            data.sat_name = document.getElementById('add_sat_name').value.toUpperCase();
        }

        fetch('/logbook/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Ошибка при добавлении QSO');
                });
            }
            return response.json();
        })
        .then(data => {
            this.disabled = false;
            this.innerHTML = '<span>➕</span> Добавить QSO';

            if (data.success) {
                // Сохраняем настройки в cookies
                saveQSOsettings();

                // Показываем уведомление
                showAlert('success', 'QSO успешно добавлено');

                // Спрашиваем про добавление еще одного QSO
                setTimeout(() => {
                    // Сначала закрываем модальное окно добавления QSO
                    const addQsoModalEl = document.getElementById('addQSOModal');
                    const addQsoModal = bootstrap.Modal.getInstance(addQsoModalEl);
                    if (addQsoModal) {
                        addQsoModal.hide();
                    }

                    // Ждём немного чтобы первое модальное окно закрылось
                    setTimeout(() => {
                        // Показываем модальное окно подтверждения
                        const addAnotherModalEl = document.getElementById('addAnotherQSOModal');
                        const addAnotherModal = new bootstrap.Modal(addAnotherModalEl);
                        addAnotherModal.show();

                        // Обработчик кнопки "Добавить еще QSO"
                        document.getElementById('addAnotherQSO').onclick = function() {
                            addAnotherModal.hide();
                            // Открываем окно добавления QSO заново
                            const modal = new bootstrap.Modal(addQsoModalEl);
                            modal.show();
                            // Сбрасываем форму
                            resetAddQSOForm();
                            document.getElementById('add_callsign').focus();
                        };

                        // Обработчик кнопки "Отмена" - перезагружаем страницу
                        document.querySelector('#addAnotherQSOModal .btn-secondary').onclick = function() {
                            addAnotherModal.hide();
                            window.location.reload();
                        };
                    }, 300);
                }, 500);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(error => {
            this.disabled = false;
            this.innerHTML = '<span>➕</span> Добавить QSO';
            showAlert('danger', 'Ошибка при добавлении QSO: ' + error.message);
        });
    });
}

// Инициализация всех функций добавления QSO
function initAddQSO() {
    initAddQSOModal();
    initSatQSOCheckbox();
    initSaveAddQSO();
}

// Запускаем инициализацию при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initAddQSO();
});
