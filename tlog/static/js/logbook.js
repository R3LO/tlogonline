// ========== Основные функции для работы со страницей logbook ==========

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

// Обработка кнопок редактирования
function initEditButtons() {
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', function() {
            const qsoId = this.dataset.id;

            // Загружаем данные QSO из базы данных
            fetch(`/logbook/get/${qsoId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const qso = data.qso;

                    // Заполняем форму данными из базы
                    document.getElementById('edit_id').value = qso.id;
                    document.getElementById('edit_date').value = qso.date || '';
                    document.getElementById('edit_time').value = qso.time ? qso.time.substring(0, 5) : '';
                    document.getElementById('edit_callsign').value = qso.callsign || '';
                    document.getElementById('edit_band').value = qso.band || '';
                    document.getElementById('edit_mode').value = qso.mode || 'SSB';
                    document.getElementById('edit_frequency').value = qso.frequency || '';
                    document.getElementById('edit_rst_rcvd').value = qso.rst_rcvd || '';
                    document.getElementById('edit_rst_sent').value = qso.rst_sent || '';
                    document.getElementById('edit_my_gridsquare').value = qso.my_gridsquare || '';
                    document.getElementById('edit_gridsquare').value = qso.gridsquare || '';
                    document.getElementById('edit_sat_name').value = qso.sat_name || '';
                    document.getElementById('edit_prop_mode').value = qso.prop_mode || '';
                    document.getElementById('edit_cqz').value = qso.cqz || '';
                    document.getElementById('edit_ituz').value = qso.ituz || '';
                    document.getElementById('edit_lotw').value = qso.lotw || 'N';
                    document.getElementById('edit_continent').value = qso.continent || '';
                    document.getElementById('edit_r150s').value = qso.r150s || '';
                    document.getElementById('edit_dxcc').value = qso.dxcc || '';
                    document.getElementById('edit_ru_region').value = qso.ru_region || '';

                    document.getElementById('edit_paper_qsl').value = qso.paper_qsl || 'N';

                    // Открываем модальное окно
                    const modal = new bootstrap.Modal(document.getElementById('editQSOModal'));
                    modal.show();
                } else {
                    throw new Error(data.error || 'Ошибка при загрузке данных');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Ошибка при загрузке данных QSO: ' + error.message);
            });
        });
    });
}

// Сохранение редактирования
function initSaveEditQSO() {
    document.getElementById('saveEditQSO').addEventListener('click', function() {
        const form = document.getElementById('editQSOForm');
        const formData = new FormData(form);
        const qsoId = formData.get('id');

        this.disabled = true;
        this.innerHTML = '<span>⏳</span> Сохранение...';

        fetch(`/logbook/edit/${qsoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(Object.fromEntries(formData)),
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            this.disabled = false;
            this.innerHTML = '<span>💾</span> Сохранить';

            if (data.success) {
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('editQSOModal'));
                modal.hide();

                // Показываем уведомление
                showAlert('success', 'Запись успешно обновлена');

                // Перезагружаем страницу через 1 секунду
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(error => {
            this.disabled = false;
            this.innerHTML = '<span>💾</span> Сохранить';
            console.error('Error:', error);
            showAlert('danger', 'Ошибка при сохранении: ' + error.message);
        });
    });
}

// Обработка кнопок удаления
function initDeleteButtons() {
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function() {
            const qsoId = this.dataset.id;
            const callsign = this.dataset.callsign;
            const row = document.querySelector(`.qso-row[data-qso-id="${qsoId}"]`);

            // Заполняем информацию
            document.getElementById('delete_id').value = qsoId;
            document.getElementById('delete_callsign').textContent = callsign;

            const dateCell = row.querySelector('td:nth-child(1) small');
            const timeCell = row.querySelector('td:nth-child(2) small');
            document.getElementById('delete_date').textContent = dateCell ? dateCell.textContent : '';
            document.getElementById('delete_time').textContent = timeCell ? timeCell.textContent : '';

            // Открываем модальное окно
            const modal = new bootstrap.Modal(document.getElementById('deleteQSOModal'));
            modal.show();
        });
    });
}

// Подтверждение удаления одной записи
function initConfirmDeleteQSO() {
    document.getElementById('confirmDeleteQSO').addEventListener('click', function() {
        const qsoId = document.getElementById('delete_id').value;

        this.disabled = true;
        this.innerHTML = '<span>⏳</span> Удаление...';

        fetch(`/logbook/delete/${qsoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            this.disabled = false;
            this.innerHTML = '<span>🗑️</span> Удалить';

            if (data.success) {
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteQSOModal'));
                modal.hide();

                // Показываем уведомление
                showAlert('success', 'Запись успешно удалена');

                // Перезагружаем страницу через 1 секунду
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(error => {
            this.disabled = false;
            this.innerHTML = '<span>🗑️</span> Удалить';
            console.error('Error:', error);
            showAlert('danger', 'Ошибка при удалении: ' + error.message);
        });
    });
}

// Обработка удаления лога
function initClearLog() {
    document.getElementById('confirmClearLog')?.addEventListener('click', function() {
        this.disabled = true;
        this.innerHTML = '<span>⏳</span> Удаление...';

        fetch('/logbook/clear/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('clearLogModal'));
                modal.hide();

                // Показываем уведомление
                showAlert('success', data.message);

                // Перезагружаем страницу через 1.5 секунды
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Ошибка при удалении лога: ' + error.message);

            // Восстанавливаем кнопку
            this.disabled = false;
            this.innerHTML = '<span>🗑️</span> Удалить весь лог';
        });
    });
}

// Инициализация всех основных функций страницы logbook
function initLogbookPage() {
    initClearLog();
    initEditButtons();
    initSaveEditQSO();
    initDeleteButtons();
    initConfirmDeleteQSO();
}

// Запускаем инициализацию при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initLogbookPage();
});
