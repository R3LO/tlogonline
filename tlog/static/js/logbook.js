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

// Функция для установки куки
function setCookie(name, value, days) {
    let expires = '';
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
}

// Функция для удаления куки
function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
}

// Сохранение фильтров в куки
function saveFiltersToCookies() {
    const filterForm = document.querySelector('.filter-controls');
    if (!filterForm) return;

    const myCallsign = filterForm.querySelector('[name="my_callsign"]')?.value || '';
    const dateFrom = filterForm.querySelector('[name="date_from"]')?.value || '';
    const dateTo = filterForm.querySelector('[name="date_to"]')?.value || '';
    const searchCallsign = filterForm.querySelector('[name="search_callsign"]')?.value || '';
    const searchQth = filterForm.querySelector('[name="search_qth"]')?.value || '';
    const band = filterForm.querySelector('[name="band"]')?.value || '';
    const mode = filterForm.querySelector('[name="mode"]')?.value || '';
    const satName = filterForm.querySelector('[name="sat_name"]')?.value || '';
    const lotw = filterForm.querySelector('[name="lotw"]')?.value || '';

    setCookie('logbook_filter_my_callsign', myCallsign, 30);
    setCookie('logbook_filter_date_from', dateFrom, 30);
    setCookie('logbook_filter_date_to', dateTo, 30);
    setCookie('logbook_filter_search_callsign', searchCallsign, 30);
    setCookie('logbook_filter_search_qth', searchQth, 30);
    setCookie('logbook_filter_band', band, 30);
    setCookie('logbook_filter_mode', mode, 30);
    setCookie('logbook_filter_sat_name', satName, 30);
    setCookie('logbook_filter_lotw', lotw, 30);
}

// Восстановление фильтров из кук
function restoreFiltersFromCookies() {
    const filterForm = document.querySelector('.filter-controls');
    if (!filterForm) return;

    const myCallsignInput = filterForm.querySelector('[name="my_callsign"]');
    const dateFromInput = filterForm.querySelector('[name="date_from"]');
    const dateToInput = filterForm.querySelector('[name="date_to"]');
    const searchCallsignInput = filterForm.querySelector('[name="search_callsign"]');
    const searchQthInput = filterForm.querySelector('[name="search_qth"]');
    const bandInput = filterForm.querySelector('[name="band"]');
    const modeInput = filterForm.querySelector('[name="mode"]');
    const satNameInput = filterForm.querySelector('[name="sat_name"]');
    const lotwInput = filterForm.querySelector('[name="lotw"]');

    if (myCallsignInput) {
        const value = getCookie('logbook_filter_my_callsign') || '';
        myCallsignInput.value = value;
    }
    if (dateFromInput) {
        const value = getCookie('logbook_filter_date_from') || '';
        dateFromInput.value = value;
    }
    if (dateToInput) {
        const value = getCookie('logbook_filter_date_to') || '';
        dateToInput.value = value;
    }
    if (searchCallsignInput) {
        const value = getCookie('logbook_filter_search_callsign') || '';
        searchCallsignInput.value = value;
    }
    if (searchQthInput) {
        const value = getCookie('logbook_filter_search_qth') || '';
        searchQthInput.value = value;
    }
    if (bandInput) {
        const value = getCookie('logbook_filter_band') || '';
        bandInput.value = value;
    }
    if (modeInput) {
        const value = getCookie('logbook_filter_mode') || '';
        modeInput.value = value;
    }
    if (satNameInput) {
        const value = getCookie('logbook_filter_sat_name') || '';
        satNameInput.value = value;
    }
    if (lotwInput) {
        const value = getCookie('logbook_filter_lotw') || '';
        lotwInput.value = value;
    }
}

// Инициализация фильтров
function initFilters() {
    const filterForm = document.querySelector('.filter-controls');
    if (!filterForm) return;

    // Восстанавливаем фильтры из кук при загрузке страницы
    restoreFiltersFromCookies();

    // Сохраняем фильтры при отправке формы (независимо от метода)
    filterForm.addEventListener('submit', function(e) {
        // Сохраняем фильтры в куки перед отправкой
        saveFiltersToCookies();
    });

    // Обработка кнопки сброса фильтров
    const resetButton = filterForm.querySelector('a[href="/logbook/"]');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            // Удаляем куки фильтров при сбросе
            deleteCookie('logbook_filter_my_callsign');
            deleteCookie('logbook_filter_date_from');
            deleteCookie('logbook_filter_date_to');
            deleteCookie('logbook_filter_search_callsign');
            deleteCookie('logbook_filter_search_qth');
            deleteCookie('logbook_filter_band');
            deleteCookie('logbook_filter_mode');
            deleteCookie('logbook_filter_sat_name');
            deleteCookie('logbook_filter_lotw');
        });
    }

    // Также сохраняем фильтры при изменении полей (для автосохранения)
    const filterInputs = filterForm.querySelectorAll('select, input[type="text"], input[type="date"]');
    filterInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            saveFiltersToCookies();
        });
    });
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

// Обработка чекбокса "Добавить дополнительные теги" в модальном окне ADIF
function initAdifExtraTagsCheckbox() {
    const checkbox = document.getElementById('adif_add_extra_tags');
    const optionsDiv = document.getElementById('adif-options');
    const satOptionsDiv = document.getElementById('adif-options-sat');
    
    if (!checkbox || !optionsDiv || !satOptionsDiv) return;
    
    checkbox.addEventListener('change', function() {
        if (this.checked) {
            optionsDiv.style.display = 'flex';
            satOptionsDiv.style.display = 'flex';
        } else {
            optionsDiv.style.display = 'none';
            satOptionsDiv.style.display = 'none';
        }
    });
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
                    document.getElementById('edit_state').value = qso.state || '';
                    document.getElementById('edit_paper_qsl').value = qso.paper_qsl || 'N';

                    // Блокируем поля если QSO подтверждено в LoTW
                    const lotwConfirmed = qso.lotw === 'Y';
                    const lockedFields = ['edit_cqz', 'edit_ituz', 'edit_continent', 'edit_r150s', 'edit_dxcc', 'edit_state'];
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

                    // Заполняем модальное окно данными из базы (только для чтения)
                    const setText = (id, value) => {
                        const element = document.getElementById(id);
                        if (element) {
                            element.textContent = value || '-';
                        }
                    };

                    setText('view_id', qso.id || '-');
                    setText('view_date', qso.date || '-');
                    setText('view_time', qso.time ? qso.time.substring(0, 5) : '-');
                    setText('view_my_callsign', qso.my_callsign || '-');
                    setText('view_callsign', qso.callsign || '-');
                    setText('view_band', qso.band || '-');
                    setText('view_mode', qso.mode || '-');
                    setText('view_frequency', qso.frequency || '-');
                    setText('view_rst_rcvd', qso.rst_rcvd || '-');
                    setText('view_rst_sent', qso.rst_sent || '-');
                    setText('view_my_gridsquare', qso.my_gridsquare || '-');
                    setText('view_gridsquare', qso.gridsquare || '-');
                    setText('view_sat_name', qso.sat_name || '-');
                    setText('view_prop_mode', qso.prop_mode || '-');
                    setText('view_continent', qso.continent || '-');
                    setText('view_state', qso.state || '-');
                    setText('view_dxcc', qso.dxcc || '-');
                    setText('view_r150s', qso.r150s || '-');
                    setText('view_lotw', qso.lotw || '-');
                    setText('view_paper_qsl', qso.paper_qsl || '-');
                    setText('view_app_lotw_rxqsl', qso.app_lotw_rxqsl || '-');

                    // Открываем модальное окно просмотра
                    const modal = new bootstrap.Modal(document.getElementById('viewQSOModal'));
                    modal.show();
                } else {
                    showAlert('danger', 'Ошибка при загрузке данных QSO: ' + (data.error || 'Неизвестная ошибка'));
                }
            })
            .catch(function(error) {
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
                           'continent', 'r150s', 'dxcc', 'state'];
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
    initAdifExtraTagsCheckbox();
    initFilters();  // Добавлена инициализация фильтров

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

// Функция для удаления ADIF загрузки
function deleteAdifUpload(uploadId, fileName) {
    if (confirm(`Вы уверены, что хотите удалить файл "${fileName}" и все связанные с ним QSO?`)) {
        fetch(`/dashboard/adif-delete/${uploadId}/`, {
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
            if (data.success) {
                showAlert('success', 'Файл и связанные QSO успешно удалены');
                // Перезагружаем страницу через 1 секунду
                setTimeout(function() {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(function(error) {
            showAlert('danger', 'Ошибка при удалении файла: ' + error.message);
        });
    }
}

// ========== Функции для модального окна Cosmos Diploma ==========

// Инициализация модального окна Cosmos
function initCosmosModal() {
    const modal = document.getElementById('cosmosModal');
    if (!modal) return;

    // Загрузка данных пользователя при открытии модального окна
    modal.addEventListener('show.bs.modal', function() {
        loadCosmosUserData();
    });

    // Очистка сообщений при открытии
    modal.addEventListener('show.bs.modal', function() {
        const messagesDiv = document.getElementById('cosmosMessages');
        if (messagesDiv) {
            messagesDiv.innerHTML = '';
        }
        // Скрываем кнопку скачивания
        const downloadBtn = document.getElementById('cosmosDownloadBtn');
        if (downloadBtn) {
            downloadBtn.style.display = 'none';
        }
        // Показываем кнопку отправки
        const submitBtn = document.getElementById('cosmosSubmitBtn');
        if (submitBtn) {
            submitBtn.style.display = 'inline-block';
        }
    });
}

// Загрузка данных пользователя для формы Cosmos
function loadCosmosUserData() {
    fetch('/api/cosmos/user-data/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
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
            // Заполняем поля формы
            document.getElementById('cosmos_main_callsign').value = data.main_callsign || '';
            document.getElementById('cosmos_full_name').value = data.full_name || '';
            document.getElementById('cosmos_email').value = data.email || '';
            document.getElementById('cosmos_phone').value = data.phone || '';
            document.getElementById('cosmos_info').value = data.info || '';

            // Заполняем дополнительные позывные
            const container = document.getElementById('cosmos_callsigns_container');
            container.innerHTML = '';
            if (data.other_callsigns && data.other_callsigns.length > 0) {
                data.other_callsigns.forEach(function(callsign) {
                    addCosmosCallsign(callsign);
                });
            } else {
                // Добавляем одно пустое поле
                addCosmosCallsign();
            }
        } else {
            showAlert('danger', 'Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(function(error) {
        console.error('Error loading cosmos user data:', error);
        // В случае ошибки добавляем пустое поле
        const container = document.getElementById('cosmos_callsigns_container');
        container.innerHTML = '';
        addCosmosCallsign();
    });
}

// Добавление поля для дополнительного позывного
function addCosmosCallsign(value = '') {
    const container = document.getElementById('cosmos_callsigns_container');
    const item = document.createElement('div');
    item.className = 'my-callsign-item mb-2';
    item.innerHTML = `
        <div class="input-group">
            <input type="text" class="form-control form-control-sm callsign-input"
                   name="other_callsigns_names[]"
                   placeholder="Позывной"
                   autocomplete="off"
                   value="${value}">
            <button type="button" class="btn btn-outline-danger btn-sm btn-remove-callsign">
                ✕
            </button>
        </div>
    `;
    container.appendChild(item);

    // Добавляем обработчик для кнопки удаления
    const removeBtn = item.querySelector('.btn-remove-callsign');
    removeBtn.addEventListener('click', function() {
        item.remove();
    });

    // Добавляем обработчик для автоматического перевода в верхний регистр
    const callsignInput = item.querySelector('.callsign-input');
    callsignInput.addEventListener('input', function() {
        this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
    });
}

// Отправка формы Cosmos
function submitCosmosForm() {
    const form = document.getElementById('cosmosForm');
    const submitBtn = document.getElementById('cosmosSubmitBtn');

    // Валидация
    const mainCallsign = document.getElementById('cosmos_main_callsign').value.trim();
    const fullName = document.getElementById('cosmos_full_name').value.trim();
    const email = document.getElementById('cosmos_email').value.trim();

    if (!mainCallsign) {
        showCosmosMessage('danger', 'Позывной обязателен для заполнения');
        return;
    }

    if (!fullName) {
        showCosmosMessage('danger', 'ФИО обязательно для заполнения');
        return;
    }

    if (!email) {
        showCosmosMessage('danger', 'Email обязателен для заполнения');
        return;
    }

    // Собираем дополнительные позывные
    const callsigns = [];
    const items = document.querySelectorAll('#cosmos_callsigns_container .my-callsign-item');
    items.forEach(function(item) {
        const input = item.querySelector('input[name="other_callsigns_names[]"]');
        const name = input.value.trim().toUpperCase();
        if (name) {
            callsigns.push(name);
        }
    });

    // Формируем данные для отправки
    const formData = new FormData();
    formData.append('main_callsign', mainCallsign);
    formData.append('full_name', fullName);
    formData.append('email', email);
    formData.append('phone', document.getElementById('cosmos_phone').value.trim());
    formData.append('info', document.getElementById('cosmos_info').value.trim());
    formData.append('other_callsigns_json', JSON.stringify(callsigns));

    // Блокируем кнопку
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Формирование...';

    // Отправляем запрос
    fetch('/api/cosmos/generate/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: formData,
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
            showCosmosMessage(data.qso_count >= 100 ? 'success' : 'warning', data.message);
            // Показываем кнопку скачивания
            const downloadBtn = document.getElementById('cosmosDownloadBtn');
            if (downloadBtn) {
                downloadBtn.style.display = 'inline-block';
            }
            // Скрываем кнопку отправки
            submitBtn.style.display = 'none';
        } else {
            showCosmosMessage('danger', 'Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(function(error) {
        showCosmosMessage('danger', 'Ошибка при формировании заявки: ' + error.message);
    })
    .finally(function() {
        // Разблокируем кнопку
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>📄</span> Сформировать заявку';
    });
}

// Скачивание файла Cosmos
function downloadCosmosFile() {
    window.location.href = '/api/cosmos/download/';
}

// Показ сообщения в модальном окне Cosmos
function showCosmosMessage(type, message) {
    const messagesDiv = document.getElementById('cosmosMessages');
    messagesDiv.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initCosmosModal();
});