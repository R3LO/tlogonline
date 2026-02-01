// JavaScript для страницы LoTW с AJAX фильтрацией
document.addEventListener('DOMContentLoaded', function() {
    
    // Инициализация всех функций
    initCardAnimations();
    initStatusRefresh();
    initQuickActions();
    initTooltips();
    initAjaxFilters();
    initPaginationLoading();
    
    // Анимации для карточек
    function initCardAnimations() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach((card, index) => {
            // Добавляем задержку для каждой карточки
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }
            
    // Инициализация AJAX фильтров
    function initAjaxFilters() {
        const filterForm = document.querySelector('.filter-controls');
        const filterInputs = filterForm.querySelectorAll('select, input[type="text"]');
        const resetBtn = document.getElementById('resetFilters');
        
        // Загружаем позывные пользователя
        loadUserCallsigns();
        
        // Автофильтрация при изменении значений (с задержкой)
        let filterTimeout;
        filterInputs.forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(filterTimeout);
                filterTimeout = setTimeout(() => {
                    applyFilters();
                }, 500); // Задержка 500мс
            });
            
            input.addEventListener('change', function() {
                clearTimeout(filterTimeout);
                filterTimeout = setTimeout(() => {
                    applyFilters();
                }, 500);
            });
        });
        
        // Кнопка сброса фильтров
        if (resetBtn) {
            resetBtn.addEventListener('click', function(e) {
                e.preventDefault();
                clearFilters();
            });
        }
    }
    
    // Загрузка позывных пользователя
    async function loadUserCallsigns() {
        try {
            const response = await fetch('/api/lotw/callsigns/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success && data.callsigns) {
                const myCallsignSelect = document.querySelector('select[name="my_callsign"]');
                if (myCallsignSelect) {
                    // Сохраняем первый элемент "Все"
                    const firstOption = myCallsignSelect.querySelector('option[value=""]');
                    
                    // Очищаем существующие опции кроме первой
                    while (myCallsignSelect.children.length > 1) {
                        myCallsignSelect.removeChild(myCallsignSelect.lastChild);
                    }
                    
                    // Добавляем позывные пользователя
                    data.callsigns.forEach(callsign => {
                        const option = document.createElement('option');
                        option.value = callsign;
                        option.textContent = callsign;
                        myCallsignSelect.appendChild(option);
                    });
                    
                    console.log(`Загружено ${data.callsigns.length} позывных пользователя`);
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки позывных:', error);
        }
    }

    // Функция применения фильтров через AJAX
    function applyFilters(page = 1) {
        const filterForm = document.querySelector('.filter-controls');
        const formData = new FormData(filterForm);
        
        // Подготавливаем данные для отправки
        const filterData = {
            my_callsign: formData.get('my_callsign') || '',
            search_callsign: formData.get('search_callsign') || '',
            search_qth: formData.get('search_qth') || '',
            band: formData.get('band') || '',
            mode: formData.get('mode') || '',
            sat_name: formData.get('sat_name') || '',
            page: page
        };
        
        // Показываем индикатор загрузки
        showLoadingIndicator();
        
        // Отключаем кнопки во время загрузки
        setFormEnabled(false);
        
        // Выполняем AJAX запрос
        fetch('/api/lotw/filter/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filterData),
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            hideLoadingIndicator();
            setFormEnabled(true);
            
            if (data.success) {
                updateTableData(data);
                updatePagination(data);
                updateStats(data);
                showNotification('Фильтры применены', 'success');
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(error => {
            hideLoadingIndicator();
            setFormEnabled(true);
            console.error('Error:', error);
            showNotification('Ошибка фильтрации: ' + error.message, 'danger');
        });
    }
    
    // Обновление данных таблицы
    function updateTableData(data) {
        const tableBody = document.querySelector('.lotw-table tbody');
        if (!tableBody) return;
        
        if (data.qso_data.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="12" class="text-center text-muted py-4">
                        <div class="qso-table-empty-icon">📡</div>
                        <div class="qso-table-empty-title">Записи не найдены</div>
                        <div class="qso-table-empty-text">Попробуйте изменить параметры фильтрации</div>
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        data.qso_data.forEach(qso => {
            html += `
                <tr>
                    <td class="col-date" data-label="📅 Date">
                        <small>${qso.date}</small>
                    </td>
                    <td class="col-time" data-label="🕐 Time">
                        <small>${qso.time}</small>
                    </td>
                    <td class="col-my-callsign" data-label="👤 My Call">
                        <small>${qso.my_callsign}</small>
                    </td>
                    <td class="col-callsign" data-label="📡 Callsign">
                        <span class="callsign-badge">${qso.callsign}</span>
                    </td>
                    <td class="col-band" data-label="📶 Band">
                        ${qso.band ? 
                            `<span class="band-badge">${qso.band}</span>` : 
                            (qso.frequency ? 
                                `<span class="band-badge">${qso.frequency}</span><br><small class="text-muted">${qso.frequency} MHz</small>` : 
                                '<span class="text-muted">-</span>'
                            )
                        }
                    </td>
                    <td class="col-mode" data-label="📟 Mode">
                        <span class="mode-badge">${qso.mode}</span>
                    </td>
                    <td class="col-qth" data-label="📍 QTH">
                        ${qso.gridsquare ? `<small>${qso.gridsquare}</small>` : '<small class="text-muted">-</small>'}
                    </td>
                    <td class="col-r150s" data-label="🏆 Р-150-С">
                        ${qso.r150s ? qso.r150s : '<small class="text-muted">-</small>'}
                    </td>
                    <td class="col-region" data-label="🇷🇺 RU">
                        ${qso.ru_region ? 
                            `<span class="region-badge" title="${qso.ru_region}">${qso.ru_region}</span>` : 
                            '<small class="text-muted">-</small>'
                        }
                    </td>
                    <td class="col-propsat" data-label="📡 PROP/SAT">
                        ${(qso.prop_mode || qso.sat_name) ? 
                            `<small>${qso.prop_mode || ''}${(qso.prop_mode && qso.sat_name) ? ' / ' : ''}${qso.sat_name || ''}</small>` : 
                            '<small class="text-muted">-</small>'
                        }
                    </td>
                    <td class="col-lotw-date" data-label="📧 LoTW">
                        <span class="lotw-date-badge">${qso.lotw_date}</span>
                    </td>
                    <td class="col-lotw" data-label="LoTW">
                        <span class="lotw-confirmed" title="LoTW Confirmed">✅</span>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }

    // Обновление пагинации
    function updatePagination(data) {
        const pagination = document.querySelector('.pagination');
        const paginationInfo = document.querySelector('.pagination-info');
        
        if (!pagination) return;
        
        // Обновляем информацию о страницах
        if (paginationInfo) {
            paginationInfo.innerHTML = `
                <small>
                    Страница ${data.current_page} из ${data.total_pages} 
                    (${data.qso_data.length} из ${data.total_count} записей)
                </small>
            `;
        }
        
        // Обновляем пагинацию если нужно
        if (data.total_pages <= 1) {
            pagination.style.display = 'none';
            return;
        }
        
        pagination.style.display = 'flex';
        
        // Получаем текущие фильтры для сохранения в пагинации
        const filterForm = document.querySelector('.filter-controls');
        const formData = new FormData(filterForm);
        const filters = {
            my_callsign: formData.get('my_callsign') || '',
            search_callsign: formData.get('search_callsign') || '',
            search_qth: formData.get('search_qth') || '',
            band: formData.get('band') || '',
            mode: formData.get('mode') || '',
            sat_name: formData.get('sat_name') || ''
        };
        
        // Создаем пагинацию
        let paginationHtml = '';
        
        // Предыдущая страница
        if (data.current_page > 1) {
            paginationHtml += `
                <li class="page-item">
                    <a class="page-link btn-link" href="#" data-page="${data.current_page - 1}">Предыдущая</a>
                </li>
            `;
        }
        
        // Номера страниц (упрощенная версия)
        for (let i = 1; i <= Math.min(data.total_pages, 5); i++) {
            if (i === data.current_page) {
                paginationHtml += `
                    <li class="page-item active">
                        <span class="page-link">${i}</span>
                    </li>
                `;
            } else {
                paginationHtml += `
                    <li class="page-item">
                        <a class="page-link btn-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            }
        }
        
        // Следующая страница
        if (data.current_page < data.total_pages) {
            paginationHtml += `
                <li class="page-item">
                    <a class="page-link btn-link" href="#" data-page="${data.current_page + 1}">Следующая</a>
                </li>
            `;
        }
        
        pagination.innerHTML = paginationHtml;
        
        // Добавляем обработчики для новых ссылок пагинации
        pagination.querySelectorAll('.page-link[data-page]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = parseInt(this.dataset.page);
                applyFilters(page);
            });
        });
    }

    // Обновление статистики
    function updateStats(data) {
        // Обновляем счетчики если есть элементы
        const totalElements = document.querySelectorAll('[data-total-count]');
        totalElements.forEach(el => {
            el.textContent = data.total_count;
        });
    
        const dxccElements = document.querySelectorAll('[data-dxcc-count]');
        dxccElements.forEach(el => {
            el.textContent = data.dxcc_entities;
        });
    
        const awardElements = document.querySelectorAll('[data-award-credits]');
        awardElements.forEach(el => {
            el.textContent = data.award_credits;
        });
    }
    
    // Функция очистки фильтров
    function clearFilters() {
        const filterForm = document.querySelector('.filter-controls');
        const inputs = filterForm.querySelectorAll('input[type="text"], select');
        
        // Очищаем все поля
        inputs.forEach(input => {
            if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            } else {
                input.value = '';
            }
        });
        
        // Показываем уведомление
        showNotification('Фильтры сброшены', 'info');
        
        // Применяем очищенные фильтры
        applyFilters(1);
    }
    
    // Обновление статуса LoTW
    function initStatusRefresh() {
        const statusElements = document.querySelectorAll('.lotw-status');
        
        statusElements.forEach(element => {
            // Добавляем кнопку обновления если есть статус
            const refreshBtn = document.createElement('button');
            refreshBtn.className = 'btn btn-sm btn-outline-primary ms-2';
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Обновить';
            refreshBtn.onclick = refreshLoTWStatus;
            
            const statusContainer = element.querySelector('.alert');
            if (statusContainer) {
                statusContainer.appendChild(refreshBtn);
            }
        });
    }
    
    // Функция обновления статуса LoTW
    async function refreshLoTWStatus() {
        const btn = event.target;
        const originalText = btn.innerHTML;
        
        // Показываем загрузку
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обновление...';
        btn.disabled = true;
        
        try {
            // Здесь можно добавить AJAX запрос для обновления статуса
            // const response = await fetch('/api/lotw/status/refresh/', {
            //     method: 'POST',
            //     headers: {
            //         'X-CSRFToken': getCsrfToken(),
            //         'Content-Type': 'application/json'
            //     }
            // });
            
            // Имитация задержки
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Показать уведомление об успехе
            showNotification('Статус LoTW обновлен!', 'success');
            
            // Перезагрузить страницу для обновления данных
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('Ошибка обновления статуса:', error);
            showNotification('Ошибка обновления статуса', 'error');
        } finally {
            // Восстановить кнопку
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }
    
    // Инициализация быстрых действий
    function initQuickActions() {
        const actionButtons = document.querySelectorAll('.quick-actions .btn');
        
        actionButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Добавляем визуальную обратную связь
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 1000);
            });
        });
    }
    
    // Инициализация tooltips
    function initTooltips() {
        // Инициализация Bootstrap tooltips если они используются
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Утилиты
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    function setFormEnabled(enabled) {
        const filterForm = document.querySelector('.filter-controls');
        const inputs = filterForm.querySelectorAll('input, select, button');
        
        inputs.forEach(input => {
            input.disabled = !enabled;
        });
    }
    
    function showNotification(message, type = 'info') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Плавная прокрутка к элементам
    function smoothScrollTo(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
    
    // Индикатор загрузки для пагинации
    function initPaginationLoading() {
        const paginationLinks = document.querySelectorAll('.pagination .page-link');
        
        paginationLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Показываем индикатор загрузки
                showLoadingIndicator();
                
                // Скрываем индикатор через 2 секунды (если страница не загрузилась)
                setTimeout(() => {
                    hideLoadingIndicator();
                }, 2000);
            });
        });
    }

    function showLoadingIndicator() {
        let overlay = document.querySelector('.loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Загрузка...</div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.classList.add('show');
    }

    function hideLoadingIndicator() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    
    // Экспортируем функции для глобального использования
    window.LoTW = {
        applyFilters: applyFilters,
        clearFilters: clearFilters,
        refreshStatus: refreshLoTWStatus,
        showNotification: showNotification,
        smoothScrollTo: smoothScrollTo,
        showLoading: showLoadingIndicator,
        hideLoading: hideLoadingIndicator
    };
});