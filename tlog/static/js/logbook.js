// ========== Основной JS код для logbook ==========

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
    alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    document.body.appendChild(alertDiv);
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Обработка кнопок редактирования
function initEditButtons() {
    document.querySelectorAll('.btn-edit').forEach(function(button) {
        button.addEventListener('click', function() {
            const qsoId = this.dataset.id;

            // Загружаем данные QSO из базы данных
            fetch('/logbook/get/' + qsoId + '/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    const qso = data.qso;

                    // Заполняем форму данными из базы
                    document.getElementById('edit_id').value = qso.id || '';
                    document.getElementById('edit_date').value = qso.date || '';
                    document.getElementById('edit_time').value = qso.time ? qso.time.substring(0, 5) : '';
                    document.getElementById('edit_my_callsign').value = qso.my_callsign || '';
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
                    document.getElementById('edit_continent').value = qso.continent || '';
                    document.getElementById('edit_r150s').value = qso.r150s || '';
                    document.getElementById('edit_dxcc').value = qso.dxcc || '';
                    document.getElementById('edit_ru_region').value = qso.ru_region || '';
                    document.getElementById('edit_paper_qsl').value = qso.paper_qsl || 'N';

                    // Блокируем поля если QSO подтверждено в LoTW
                    const lotwConfirmed = qso.lotw === 'Y';
                    const lockedFields = ['edit_cqz', 'edit_ituz', 'edit_continent', 'edit_r150s', 'edit_dxcc', 'edit_ru_region'];
                    lockedFields.forEach(function(fieldId) {
                        const field = document.getElementById(fieldId);
                        field.disabled = lotwConfirmed;
                        if (lotwConfirmed) {
                            field.style.backgroundColor = '#e9ecef';
                        } else {
                            field.style.backgroundColor = '';
                        }
                    });

                    // Показываем бейдж LoTW если подтверждено
                    const lotwBadge = document.getElementById('edit_lotw_badge');
                    const lotwWarning = document.getElementById('edit_lotw_warning');
                    if (lotwConfirmed) {
                        lotwBadge.style.display = 'inline-block';
                        lotwWarning.style.display = 'block';
                    } else {
                        lotwBadge.style.display = 'none';
                        lotwWarning.style.display = 'none';
                    }

                    // Открываем модальное окно
                    const modal = new bootstrap.Modal(document.getElementById('editQSOModal'));
                    modal.show();
                } else {
                    showAlert('danger', 'Ошибка при загрузке данных QSO: ' + (data.error || 'Неизвестная ошибка'));
                }
            })
            .catch(function(error) {
                console.error('Error:', error);
                showAlert('danger', 'Ошибка при загрузке данных QSO: ' + error.message);
            });
        });
    });
}

// Обработка кнопок просмотра (для LoTW записей)
function initViewButtons() {
    document.querySelectorAll('.btn-view').forEach(function(button) {
        button.addEventListener('click', function() {
            const qsoId = this.dataset.id;

            // Загружаем данные QSO из базы данных
            fetch('/logbook/get/' + qsoId + '/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    const qso = data.qso;

                    // Заполняем форму данными из базы (только для чтения)
                    document.getElementById('view_id').value = qso.id || '';
                    document.getElementById('view_date').value = qso.date || '';
                    document.getElementById('view_time').value = qso.time ? qso.time.substring(0, 5) : '';
                    document.getElementById('view_my_callsign').value = qso.my_callsign || '';
                    document.getElementById('view_callsign').value = qso.callsign || '';

                    document.getElementById('view_band').value = qso.band || '';
                    document.getElementById('view_mode').value = qso.mode || 'SSB';
                    document.getElementById('view_frequency').value = qso.frequency || '';
                    document.getElementById('view_rst_rcvd').value = qso.rst_rcvd || '';
                    document.getElementById('view_rst_sent').value = qso.rst_sent || '';
                    document.getElementById('view_my_gridsquare').value = qso.my_gridsquare || '';
                    document.getElementById('view_gridsquare').value = qso.gridsquare || '';
                    document.getElementById('view_sat_name').value = qso.sat_name || '';
                    document.getElementById('view_prop_mode').value = qso.prop_mode || '';
                    document.getElementById('view_cqz').value = qso.cqz || '';
                    document.getElementById('view_ituz').value = qso.ituz || '';
                    document.getElementById('view_continent').value = qso.continent || '';
                    document.getElementById('view_r150s').value = qso.r150s || '';
                    document.getElementById('view_dxcc').value = qso.dxcc || '';
                    document.getElementById('view_ru_region').value = qso.ru_region || '';
                    document.getElementById('view_paper_qsl').value = qso.paper_qsl || 'N';

                    // Открываем модальное окно просмотра
                    const modal = new bootstrap.Modal(document.getElementById('viewQSOModal'));
                    modal.show();
                } else {
                    showAlert('danger', 'Ошибка при загрузке данных QSO: ' + (data.error || 'Неизвестная ошибка'));
                }
            })
            .catch(function(error) {
                console.error('Error:', error);
                showAlert('danger', 'Ошибка при загрузке данных QSO: ' + error.message);
            });
        });
    });
}

// Сохранение редактирования
function initSaveEditQSO() {
    const saveBtn = document.getElementById('saveEditQSO');
    if (!saveBtn) return;

    saveBtn.addEventListener('click', function() {
        const form = document.getElementById('editQSOForm');
        const formData = new FormData(form);
        const qsoId = formData.get('id');

        // Преобразуем текстовые поля в верхний регистр
        const textFields = ['my_callsign', 'callsign', 'band', 'mode', 'rst_rcvd', 'rst_sent',
                           'gridsquare', 'my_gridsquare', 'sat_name', 'prop_mode',
                           'continent', 'r150s', 'dxcc', 'ru_region'];
        textFields.forEach(function(fieldName) {
            const field = form.querySelector('[name="' + fieldName + '"]');
            if (field && field.value) {
                formData.set(fieldName, field.value.toUpperCase());
            }
        });

        this.disabled = true;
        this.innerHTML = '<span>⏳</span> Сохранение...';

        fetch('/logbook/edit/' + qsoId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(Object.fromEntries(formData)),
            credentials: 'same-origin'
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            this.disabled = false;
            this.innerHTML = '<span>💾</span> Сохранить';

            if (data.success) {
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('editQSOModal'));
                modal.hide();

                // Показываем уведомление
                showAlert('success', 'Запись успешно обновлена');

                // Перезагружаем страницу через 1 секунду
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        }.bind(this))
        .catch(function(error) {
            this.disabled = false;
            this.innerHTML = '<span>💾</span> Сохранить';
            console.error('Error:', error);
            showAlert('danger', 'Ошибка при сохранении: ' + error.message);
        }.bind(this));
    });
}

// Обработка кнопок удаления
function initDeleteButtons() {
    document.querySelectorAll('.btn-delete').forEach(function(button) {
        button.addEventListener('click', function() {
            const qsoId = this.dataset.id;
            const callsign = this.dataset.callsign;
            const row = document.querySelector('.qso-row[data-qso-id="' + qsoId + '"]');

            // Сначала проверяем LoTW статус через API
            fetch('/logbook/get/' + qsoId + '/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                return response.json();
            })
            .then(function(data) {
                if (data.success && data.qso.lotw === 'Y') {
                    showAlert('warning', 'Подтверждения LoTW удалить нельзя');
                    return;
                }

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
            })
            .catch(function(error) {
                console.error('Error:', error);
                showAlert('danger', 'Ошибка при проверке статуса LoTW');
            });
        });
    });
}

// Подтверждение удаления одной записи
function initConfirmDeleteQSO() {
    const confirmBtn = document.getElementById('confirmDeleteQSO');
    if (!confirmBtn) return;

    confirmBtn.addEventListener('click', function() {
        const qsoId = document.getElementById('delete_id').value;

        this.disabled = true;
        this.innerHTML = '<span>⏳</span> Удаление...';

        fetch('/logbook/delete/' + qsoId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            this.disabled = false;
            this.innerHTML = '<span>🗑️</span> Удалить';

            if (data.success) {
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteQSOModal'));
                modal.hide();

                // Показываем уведомление
                showAlert('success', 'Запись успешно удалена');

                // Перезагружаем страницу через 1 секунду
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        }.bind(this))
        .catch(function(error) {
            this.disabled = false;
            this.innerHTML = '<span>🗑️</span> Удалить';
            console.error('Error:', error);
            showAlert('danger', 'Ошибка при удалении: ' + error.message);
        }.bind(this));
    });
}

// Обработка удаления лога
function initClearLog() {
    const clearBtn = document.getElementById('confirmClearLog');
    if (!clearBtn) return;

    clearBtn.addEventListener('click', function() {
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
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success) {
                // Закрываем модальное окно
                const modal = bootstrap.Modal.getInstance(document.getElementById('clearLogModal'));
                modal.hide();

                // Показываем уведомление
                showAlert('success', data.message);

                // Перезагружаем страницу через 1.5 секунды
                setTimeout(function() {
                    window.location.reload();
                }, 1500);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(function(error) {
            console.error('Error:', error);
            showAlert('danger', 'Ошибка при удалении лога: ' + error.message);

            // Восстанавливаем кнопку
            this.disabled = false;
            this.innerHTML = '<span>🗑️</span> Удалить весь лог';
        }.bind(this));
    });
}

// Инициализация всех основных функций страницы logbook
function initLogbookPage() {
    initClearLog();
    initEditButtons();
    initViewButtons();
    initSaveEditQSO();
    initDeleteButtons();
    initConfirmDeleteQSO();

    // Сбрасываем бейдж LoTW при закрытии модального окна редактирования
    const editModal = document.getElementById('editQSOModal');
    if (editModal) {
        editModal.addEventListener('hidden.bs.modal', function() {
            document.getElementById('edit_lotw_badge').style.display = 'none';
            document.getElementById('edit_lotw_warning').style.display = 'none';
        });
    }
}

// Запускаем инициализацию при загрузке страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLogbookPage);
} else {
    initLogbookPage();
}