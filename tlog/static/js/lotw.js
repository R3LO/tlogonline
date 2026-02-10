document.addEventListener('DOMContentLoaded', function() {
    
    // Функция для получения значения из куки
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
        
        // Сохраняем значения полей фильтра
        const myCallsign = filterForm.querySelector('[name="my_callsign"]')?.value || '';
        const searchCallsign = filterForm.querySelector('[name="search_callsign"]')?.value || '';
        const searchQth = filterForm.querySelector('[name="search_qth"]')?.value || '';
        const band = filterForm.querySelector('[name="band"]')?.value || '';
        const mode = filterForm.querySelector('[name="mode"]')?.value || '';
        const satName = filterForm.querySelector('[name="sat_name"]')?.value || '';

        // Сохраняем в куки (на 30 дней)
        setCookie('lotw_filter_my_callsign', myCallsign, 30);
        setCookie('lotw_filter_search_callsign', searchCallsign, 30);
        setCookie('lotw_filter_search_qth', searchQth, 30);
        setCookie('lotw_filter_band', band, 30);
        setCookie('lotw_filter_mode', mode, 30);
        setCookie('lotw_filter_sat_name', satName, 30);
    }

    // Восстановление фильтров из кук
    function restoreFiltersFromCookies() {
        const filterForm = document.querySelector('.filter-controls');
        if (!filterForm) return;

        // Восстанавливаем значения полей фильтра
        const myCallsignInput = filterForm.querySelector('[name="my_callsign"]');
        const searchCallsignInput = filterForm.querySelector('[name="search_callsign"]');
        const searchQthInput = filterForm.querySelector('[name="search_qth"]');
        const bandInput = filterForm.querySelector('[name="band"]');
        const modeInput = filterForm.querySelector('[name="mode"]');
        const satNameInput = filterForm.querySelector('[name="sat_name"]');

        if (myCallsignInput) {
            const value = getCookie('lotw_filter_my_callsign') || '';
            myCallsignInput.value = value;
        }
        if (searchCallsignInput) {
            const value = getCookie('lotw_filter_search_callsign') || '';
            searchCallsignInput.value = value;
        }
        if (searchQthInput) {
            const value = getCookie('lotw_filter_search_qth') || '';
            searchQthInput.value = value;
        }
        if (bandInput) {
            const value = getCookie('lotw_filter_band') || '';
            bandInput.value = value;
        }
        if (modeInput) {
            const value = getCookie('lotw_filter_mode') || '';
            modeInput.value = value;
        }
        if (satNameInput) {
            const value = getCookie('lotw_filter_sat_name') || '';
            satNameInput.value = value;
        }
    }

    // Инициализация фильтров
    function initFilters() {
        const filterForm = document.querySelector('.filter-controls');
        if (!filterForm) return;

        // Восстанавливаем фильтры из кук при загрузке страницы
        restoreFiltersFromCookies();

        // Сохраняем фильтры при отправке формы
        filterForm.addEventListener('submit', function(e) {
            const action = e.submitter?.value;
            if (action === 'reset') {
                // Удаляем куки фильтров при сбросе
                deleteCookie('lotw_filter_my_callsign');
                deleteCookie('lotw_filter_search_callsign');
                deleteCookie('lotw_filter_search_qth');
                deleteCookie('lotw_filter_band');
                deleteCookie('lotw_filter_mode');
                deleteCookie('lotw_filter_sat_name');
            } else {
                // Сохраняем фильтры при поиске
                saveFiltersToCookies();
            }
        });
    }

    // Инициализируем фильтры
    initFilters();

    // Функция для загрузки данных QSO
    async function loadQSODetails(qsoId) {
        try {
            // Показываем загрузку
            populateViewModal({
                id: qsoId,
                callsign: 'Загрузка...',
                date: 'Загрузка...',
                time: 'Загрузка...',
                band: 'Загрузка...',
                mode: 'Загрузка...',
                frequency: 'Загрузка...',
                rst_sent: 'Загрузка...',
                rst_rcvd: 'Загрузка...'
            });
            
            // Пытаемся получить данные с сервера
            const response = await fetch(`/api/lotw/qso-details/?qso_id=${qsoId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.status === 302) {
                // Требуется авторизация - показываем тестовые данные
                populateViewModal({
                    id: qsoId,
                    callsign: 'TEST_CALL',
                    date: '2024-01-01',
                    time: '12:00',
                    band: '20m',
                    mode: 'SSB',
                    frequency: '14.200 MHz',
                    rst_sent: '59',
                    rst_rcvd: '59',
                    my_callsign: 'MY_CALL',
                    my_gridsquare: 'JN45',
                    gridsquare: 'LO01',
                    continent: 'EU',
                    state: 'Московская область',
                    sat_name: 'AO-91',
                    prop_mode: 'SAT',
                    dxcc: '297',
                    iota: 'EU-015',
                    lotw: 'Y',
                    paper_qsl: 'N',
                    r150s: 'N',
                    app_lotw_rxqsl: '2024-01-02 14:30:00'
                });
            } else {
                const data = await response.json();
                if (data.success) {
                    populateViewModal(data.qso_data);
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            }
        } catch (error) {
            // Показываем тестовые данные при ошибке
            populateViewModal({
                id: qsoId,
                callsign: 'TEST_CALL',
                date: '2024-01-01',
                time: '12:00',
                band: '20m',
                mode: 'SSB',
                frequency: '14.200 MHz',
                rst_sent: '59',
                rst_rcvd: '59',
                my_callsign: 'MY_CALL',
                my_gridsquare: 'JN45',
                gridsquare: 'LO01',
                continent: 'EU',
                state: 'Московская область',
                sat_name: 'AO-91',
                prop_mode: 'SAT',
                dxcc: '297',
                iota: 'EU-015',
                lotw: 'Y',
                paper_qsl: 'N',
                r150s: 'N',
                app_lotw_rxqsl: '2024-01-02 14:30:00'
            });
        }
    }
            
    // Функция для заполнения модального окна
    function populateViewModal(qsoData) {
        const fields = {
            'view_id': qsoData.id || '-',
            'view_callsign': qsoData.callsign || '-',
            'view_date': qsoData.date || '-',
            'view_time': qsoData.time || '-',
            'view_band': qsoData.band || '-',
            'view_mode': qsoData.mode || '-',
            'view_frequency': qsoData.frequency || '-',
            'view_rst_sent': qsoData.rst_sent || '-',
            'view_rst_rcvd': qsoData.rst_rcvd || '-',
            'view_my_callsign': qsoData.my_callsign || '-',
            'view_my_gridsquare': qsoData.my_gridsquare || '-',
            'view_gridsquare': qsoData.gridsquare || '-',
            'view_continent': qsoData.continent || '-',
            'view_state': qsoData.state || '-',
            'view_sat_name': qsoData.sat_name || '-',
            'view_prop_mode': qsoData.prop_mode || '-',
            'view_dxcc': qsoData.dxcc || '-',
            'view_iota': qsoData.iota || '-',
            'view_lotw': qsoData.lotw || '-',
            'view_paper_qsl': qsoData.paper_qsl || '-',
            'view_r150s': qsoData.r150s || '-',
            'view_app_lotw_rxqsl': qsoData.app_lotw_rxqsl || '-'
        };
        
        Object.keys(fields).forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.textContent = fields[fieldId];
            }
        });
    }
    
    // Функция очистки фильтров
    function clearFilters() {
        const filterForm = document.getElementById('filterForm');
        if (filterForm) {
            // Очищаем все поля формы
            const inputs = filterForm.querySelectorAll('input[type="text"], select');
            inputs.forEach(input => {
                if (input.type === 'text') {
                    input.value = '';
                } else if (input.tagName === 'SELECT') {
                    input.selectedIndex = 0;
                }
            });
            
            // Отправляем форму для очистки
            filterForm.submit();
        }
    }

    // Функция для показа модального окна
    function showQSOModal(qsoId) {
        const modal = document.getElementById('viewQSOModal');
        
        if (!modal) {
            alert('Модальное окно не найдено!');
            return;
        }
        
        if (typeof bootstrap === 'undefined') {
            alert('Bootstrap не загружен!');
            return;
        }
        
        try {
            // Загружаем данные перед показом модального окна
            loadQSODetails(qsoId);
            
            const bsModal = new bootstrap.Modal(modal, {
                backdrop: true,
                keyboard: true,
                focus: true
            });
            bsModal.show();
            
            // Убираем backdrop при закрытии
            modal.addEventListener('hidden.bs.modal', function () {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
            });
            
        } catch (error) {
            alert('Ошибка показа модального окна: ' + error.message);
        }
    }
    
    // Функция для получения CSRF токена
    function getCsrfToken() {
        const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieMatch) return cookieMatch[1];
        
        const metaMatch = document.querySelector('meta[name="csrf-token"]');
        if (metaMatch) return metaMatch.getAttribute('content');
        
        const inputMatch = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (inputMatch) return inputMatch.value;
        
        return '';
    }
    
    // Глобальная функция для показа модального окна
    window.showSimpleModal = function(qsoId) {
        if (qsoId) {
            showQSOModal(qsoId);
        } else {
            showQSOModal('test-id');
        }
    };
    
    // Глобальная функция для очистки фильтров
    window.clearFilters = clearFilters;
    
    // Инициализируем фильтры
    initFilters();
    
    // Обработчики кнопок
    const viewButtons = document.querySelectorAll('.view-qso-btn');
    
    viewButtons.forEach((button, index) => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const qsoId = this.getAttribute('data-qso-id');
            
            showQSOModal(qsoId);
        });
    });
    
    // Глобальный обработчик
    document.addEventListener('click', function(e) {
        if (e.target.closest('.view-qso-btn')) {
            e.preventDefault();
            const button = e.target.closest('.view-qso-btn');
            const qsoId = button.getAttribute('data-qso-id');
            
            showQSOModal(qsoId);
        }
    });
    
    // Обработчик для отправки формы по нажатию Enter во всех полях ввода
    function setupEnterKeyFormSubmission() {
        const filterForm = document.querySelector('.filter-controls');
        if (!filterForm) return;
        
        // Находим все поля ввода в форме (кроме кнопок)
        const formInputs = filterForm.querySelectorAll('input:not([type="hidden"]), select');
        
        formInputs.forEach(input => {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    // Имитируем клик по кнопке поиска
                    const searchButton = filterForm.querySelector('button[name="action"][value="search"]');
                    if (searchButton) {
                        searchButton.click();
                    }
                }
            });
        });
    }
    
    // Инициализируем обработчик после загрузки DOM
    setupEnterKeyFormSubmission();
    
    // ========== Функции для модального окна регионов России ==========

    // Инициализация модального окна регионов
    function initLotwRegionsModal() {
        const modal = document.getElementById('lotwRegionsModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwRegionsData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            // Проверяем, есть ли другие открытые модальные окна (например, детализация региона)
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                // Удаляем backdrop только если нет других открытых модальных окон
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                // Удаляем класс с body
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            // Удаляем класс show из всех модальных окон
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных регионов с учетом фильтров
    async function loadLotwRegionsData() {
        const contentDiv = document.getElementById('lotwRegionsContent');
        if (!contentDiv) return;

        // Показываем индикатор загрузки
        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных регионов...</p>
            </div>
        `;

        try {
            // Получаем текущие значения фильтров
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            // Формируем URL с параметрами фильтров
            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/regions/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwRegionsTable(data.ratings, data.total_regions, data.filters);
            } else {
                showError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw regions:', error);
            showError('Ошибка при загрузке данных регионов: ' + error.message);
        }
    }

    // Рендеринг таблицы регионов
    function renderLotwRegionsTable(ratings, totalRegions, filters) {
        const contentDiv = document.getElementById('lotwRegionsContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        // Формируем строку с активными фильтрами
        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        // Формируем HTML для таблицы
        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего регионов:</strong> ${totalRegions}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Регионов</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-regions='${JSON.stringify(item.regions).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        // Добавляем обработчики для кнопок с количеством регионов
        setupRegionDetailButtons();
    }

    // Настройка кнопок для показа деталей по регионам
    function setupRegionDetailButtons() {
        const buttons = document.querySelectorAll('#lotwRegionsContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                // Предотвращаем всплытие события и закрытие родительского модального окна
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const regions = JSON.parse(this.getAttribute('data-regions'));
                showRegionDetailModal(callsign, regions);
            });
        });
    }

    // Показ модального окна с деталями по регионам для позывного
    function showRegionDetailModal(callsign, regions) {
        // Проверяем, существует ли модальное окно
        let modal = document.getElementById('lotwRegionDetailModal');
        if (!modal) {
            // Создаем модальное окно динамически
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwRegionDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Регионы РФ
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего регионов: <strong>${regions.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 200px;">Регион</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${regions.map((region, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${region.code}</span>
                                                        <span class="region-name">${region.name}</span>
                                                    </td>
                                                    <td>
                                                        ${region.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwRegionDetailModal');
        } else {
            // Обновляем содержимое существующего модального окна
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Регионы РФ`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего регионов: <strong>${regions.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 200px;">Регион</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${regions.map((region, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${region.code}</span>
                                        <span class="region-name">${region.name}</span>
                                    </td>
                                    <td>
                                        ${region.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        // Показываем модальное окно (Bootstrap автоматически управляет backdrop для вложенных модальных окон)
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки
    function showError(message) {
        const contentDiv = document.getElementById('lotwRegionsContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно регионов
    initLotwRegionsModal();

    // ========== Функции для модального окна штатов USA ==========

    // Инициализация модального окна штатов USA
    function initLotwUSAStatesModal() {
        const modal = document.getElementById('lotwUSAStatesModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwUSAStatesData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            // Проверяем, есть ли другие открытые модальные окна
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                // Удаляем backdrop только если нет других открытых модальных окон
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                // Удаляем класс с body
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            // Удаляем класс show из всех модальных окон
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных штатов USA с учетом фильтров
    async function loadLotwUSAStatesData() {
        const contentDiv = document.getElementById('lotwUSAStatesContent');
        if (!contentDiv) return;

        // Показываем индикатор загрузки
        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных штатов...</p>
            </div>
        `;

        try {
            // Получаем текущие значения фильтров
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            // Формируем URL с параметрами фильтров
            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/usa-states/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwUSAStatesTable(data.ratings, data.total_states, data.filters);
            } else {
                showUSAStatesError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw usa states:', error);
            showUSAStatesError('Ошибка при загрузке данных штатов: ' + error.message);
        }
    }

    // Рендеринг таблицы штатов USA
    function renderLotwUSAStatesTable(ratings, totalStates, filters) {
        const contentDiv = document.getElementById('lotwUSAStatesContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        // Формируем строку с активными фильтрами
        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        // Формируем HTML для таблицы
        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего штатов:</strong> ${totalStates}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Штатов</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-states='${JSON.stringify(item.states).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        // Добавляем обработчики для кнопок с количеством штатов
        setupUSAStateDetailButtons();
    }

    // Настройка кнопок для показа деталей по штатам
    function setupUSAStateDetailButtons() {
        const buttons = document.querySelectorAll('#lotwUSAStatesContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                // Предотвращаем всплытие события и закрытие родительского модального окна
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const states = JSON.parse(this.getAttribute('data-states'));
                showUSAStateDetailModal(callsign, states);
            });
        });
    }

    // Показ модального окна с деталями по штатам для позывного
    function showUSAStateDetailModal(callsign, states) {
        // Проверяем, существует ли модальное окно
        let modal = document.getElementById('lotwUSAStateDetailModal');
        if (!modal) {
            // Создаем модальное окно динамически
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwUSAStateDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Штаты USA
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего штатов: <strong>${states.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 80px;">Штат</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${states.map((state, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${state.code}</span>
                                                    </td>
                                                    <td>
                                                        ${state.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwUSAStateDetailModal');
        } else {
            // Обновляем содержимое существующего модального окна
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Штаты USA`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего штатов: <strong>${states.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 80px;">Штат</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${states.map((state, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${state.code}</span>
                                    </td>
                                    <td>
                                        ${state.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        // Показываем модальное окно
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для USA штатов
    function showUSAStatesError(message) {
        const contentDiv = document.getElementById('lotwUSAStatesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно штатов USA
    initLotwUSAStatesModal();

    // Инициализация модального окна провинций Китая
    function initLotwChinaProvincesModal() {
        const modal = document.getElementById('lotwChinaProvincesModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwChinaProvincesData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных провинций Китая с учетом фильтров
    async function loadLotwChinaProvincesData() {
        const contentDiv = document.getElementById('lotwChinaProvincesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных провинций...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/china-provinces/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwChinaProvincesTable(data.ratings, data.total_provinces, data.filters);
            } else {
                showChinaProvincesError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw china provinces:', error);
            showChinaProvincesError('Ошибка при загрузке данных провинций: ' + error.message);
        }
    }

    // Рендеринг таблицы провинций Китая
    function renderLotwChinaProvincesTable(ratings, totalProvinces, filters) {
        const contentDiv = document.getElementById('lotwChinaProvincesContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего провинций:</strong> ${totalProvinces}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Провинций</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-provinces='${JSON.stringify(item.provinces).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupChinaProvinceDetailButtons();
    }

    // Настройка кнопок для показа деталей по провинциям
    function setupChinaProvinceDetailButtons() {
        const buttons = document.querySelectorAll('#lotwChinaProvincesContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const provinces = JSON.parse(this.getAttribute('data-provinces'));
                showChinaProvinceDetailModal(callsign, provinces);
            });
        });
    }

    // Показ модального окна с деталями по провинциям для позывного
    function showChinaProvinceDetailModal(callsign, provinces) {
        let modal = document.getElementById('lotwChinaProvinceDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwChinaProvinceDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Провинции Китая
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего провинций: <strong>${provinces.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 80px;">Провинция</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${provinces.map((province, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${province.code}</span>
                                                    </td>
                                                    <td>
                                                        ${province.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwChinaProvinceDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Провинции Китая`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего провинций: <strong>${provinces.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 80px;">Провинция</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${provinces.map((province, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${province.code}</span>
                                    </td>
                                    <td>
                                        ${province.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для провинций Китая
    function showChinaProvincesError(message) {
        const contentDiv = document.getElementById('lotwChinaProvincesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно провинций Китая
    initLotwChinaProvincesModal();

    // Инициализация модального окна префектур Японии
    function initLotwJapanPrefecturesModal() {
        const modal = document.getElementById('lotwJapanPrefecturesModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwJapanPrefecturesData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных префектур Японии с учетом фильтров
    async function loadLotwJapanPrefecturesData() {
        const contentDiv = document.getElementById('lotwJapanPrefecturesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных префектур...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/japan-prefectures/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwJapanPrefecturesTable(data.ratings, data.total_prefectures, data.filters);
            } else {
                showJapanPrefecturesError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw japan prefectures:', error);
            showJapanPrefecturesError('Ошибка при загрузке данных префектур: ' + error.message);
        }
    }

    // Рендеринг таблицы префектур Японии
    function renderLotwJapanPrefecturesTable(ratings, totalPrefectures, filters) {
        const contentDiv = document.getElementById('lotwJapanPrefecturesContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего префектур:</strong> ${totalPrefectures}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Префектур</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-prefectures='${JSON.stringify(item.prefectures).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupJapanPrefectureDetailButtons();
    }

    // Настройка кнопок для показа деталей по префектурам
    function setupJapanPrefectureDetailButtons() {
        const buttons = document.querySelectorAll('#lotwJapanPrefecturesContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const prefectures = JSON.parse(this.getAttribute('data-prefectures'));
                showJapanPrefectureDetailModal(callsign, prefectures);
            });
        });
    }

    // Показ модального окна с деталями по префектурам для позывного
    function showJapanPrefectureDetailModal(callsign, prefectures) {
        let modal = document.getElementById('lotwJapanPrefectureDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwJapanPrefectureDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Префектуры Японии
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего префектур: <strong>${prefectures.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 80px;">Префектура</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${prefectures.map((prefecture, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${prefecture.code}</span>
                                                    </td>
                                                    <td>
                                                        ${prefecture.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwJapanPrefectureDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Префектуры Японии`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего префектур: <strong>${prefectures.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 80px;">Префектура</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${prefectures.map((prefecture, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${prefecture.code}</span>
                                    </td>
                                    <td>
                                        ${prefecture.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для префектур Японии
    function showJapanPrefecturesError(message) {
        const contentDiv = document.getElementById('lotwJapanPrefecturesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно префектур Японии
    initLotwJapanPrefecturesModal();

    // Инициализация модального окна районов Австралии
    function initLotwAustraliaStatesModal() {
        const modal = document.getElementById('lotwAustraliaStatesModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwAustraliaStatesData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных районов Австралии с учетом фильтров
    async function loadLotwAustraliaStatesData() {
        const contentDiv = document.getElementById('lotwAustraliaStatesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных районов...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/australia-states/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwAustraliaStatesTable(data.ratings, data.total_states, data.filters);
            } else {
                showAustraliaStatesError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw australia states:', error);
            showAustraliaStatesError('Ошибка при загрузке данных районов: ' + error.message);
        }
    }

    // Рендеринг таблицы районов Австралии
    function renderLotwAustraliaStatesTable(ratings, totalStates, filters) {
        const contentDiv = document.getElementById('lotwAustraliaStatesContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего районов:</strong> ${totalStates}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Районов</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-states='${JSON.stringify(item.states).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupAustraliaStateDetailButtons();
    }

    // Настройка кнопок для показа деталей по районам
    function setupAustraliaStateDetailButtons() {
        const buttons = document.querySelectorAll('#lotwAustraliaStatesContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const states = JSON.parse(this.getAttribute('data-states'));
                showAustraliaStateDetailModal(callsign, states);
            });
        });
    }

    // Показ модального окна с деталями по районам для позывного
    function showAustraliaStateDetailModal(callsign, states) {
        let modal = document.getElementById('lotwAustraliaStateDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwAustraliaStateDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Районы Австралии
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего районов: <strong>${states.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 80px;">Район</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${states.map((state, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${state.code}</span>
                                                    </td>
                                                    <td>
                                                        ${state.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwAustraliaStateDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Районы Австралии`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего районов: <strong>${states.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 80px;">Район</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${states.map((state, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${state.code}</span>
                                    </td>
                                    <td>
                                        ${state.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для районов Австралии
    function showAustraliaStatesError(message) {
        const contentDiv = document.getElementById('lotwAustraliaStatesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно районов Австралии
    initLotwAustraliaStatesModal();

    // Инициализация модального окна провинций Канады
    function initLotwCanadaProvincesModal() {
        const modal = document.getElementById('lotwCanadaProvincesModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwCanadaProvincesData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных провинций Канады с учетом фильтров
    async function loadLotwCanadaProvincesData() {
        const contentDiv = document.getElementById('lotwCanadaProvincesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных провинций...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/canada-provinces/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwCanadaProvincesTable(data.ratings, data.total_provinces, data.filters);
            } else {
                showCanadaProvincesError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw canada provinces:', error);
            showCanadaProvincesError('Ошибка при загрузке данных провинций: ' + error.message);
        }
    }

    // Рендеринг таблицы провинций Канады
    function renderLotwCanadaProvincesTable(ratings, totalProvinces, filters) {
        const contentDiv = document.getElementById('lotwCanadaProvincesContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего провинций:</strong> ${totalProvinces}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Провинций</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-provinces='${JSON.stringify(item.provinces).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupCanadaProvinceDetailButtons();
    }

    // Настройка кнопок для показа деталей по провинциям
    function setupCanadaProvinceDetailButtons() {
        const buttons = document.querySelectorAll('#lotwCanadaProvincesContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const provinces = JSON.parse(this.getAttribute('data-provinces'));
                showCanadaProvinceDetailModal(callsign, provinces);
            });
        });
    }

    // Показ модального окна с деталями по провинциям для позывного
    function showCanadaProvinceDetailModal(callsign, provinces) {
        let modal = document.getElementById('lotwCanadaProvinceDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwCanadaProvinceDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Провинции Канады
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего провинций: <strong>${provinces.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 80px;">Провинция</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${provinces.map((province, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${province.code}</span>
                                                    </td>
                                                    <td>
                                                        ${province.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwCanadaProvinceDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Провинции Канады`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего провинций: <strong>${provinces.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 80px;">Провинция</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${provinces.map((province, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${province.code}</span>
                                    </td>
                                    <td>
                                        ${province.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для провинций Канады
    function showCanadaProvincesError(message) {
        const contentDiv = document.getElementById('lotwCanadaProvincesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно провинций Канады
    initLotwCanadaProvincesModal();

    // Инициализация модального окна зон CQ
    function initLotwCQZonesModal() {
        const modal = document.getElementById('lotwCQZonesModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwCQZonesData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных зон CQ с учетом фильтров
    async function loadLotwCQZonesData() {
        const contentDiv = document.getElementById('lotwCQZonesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных зон...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/cq-zones/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwCQZonesTable(data.ratings, data.total_zones, data.filters);
            } else {
                showCQZonesError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw cq zones:', error);
            showCQZonesError('Ошибка при загрузке данных зон: ' + error.message);
        }
    }

    // Рендеринг таблицы зон CQ
    function renderLotwCQZonesTable(ratings, totalZones, filters) {
        const contentDiv = document.getElementById('lotwCQZonesContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего зон:</strong> ${totalZones}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Зон</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-zones='${JSON.stringify(item.zones).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupCQZoneDetailButtons();
    }

    // Настройка кнопок для показа деталей по зонам
    function setupCQZoneDetailButtons() {
        const buttons = document.querySelectorAll('#lotwCQZonesContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const zones = JSON.parse(this.getAttribute('data-zones'));
                showCQZoneDetailModal(callsign, zones);
            });
        });
    }

    // Показ модального окна с деталями по зонам для позывного
    function showCQZoneDetailModal(callsign, zones) {
        let modal = document.getElementById('lotwCQZoneDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwCQZoneDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Зоны CQ
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего зон: <strong>${zones.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 80px;">Зона</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${zones.map((zone, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${zone.code}</span>
                                                    </td>
                                                    <td>
                                                        ${zone.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwCQZoneDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Зоны CQ`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего зон: <strong>${zones.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 80px;">Зона</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${zones.map((zone, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${zone.code}</span>
                                    </td>
                                    <td>
                                        ${zone.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для зон CQ
    function showCQZonesError(message) {
        const contentDiv = document.getElementById('lotwCQZonesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно зон CQ
    initLotwCQZonesModal();

    // Инициализация модального окна зон ITU
    function initLotwITUZonesModal() {
        const modal = document.getElementById('lotwITUZonesModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwITUZonesData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных зон ITU с учетом фильтров
    async function loadLotwITUZonesData() {
        const contentDiv = document.getElementById('lotwITUZonesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных зон...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/itu-zones/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwITUZonesTable(data.ratings, data.total_zones, data.filters);
            } else {
                showITUZonesError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw itu zones:', error);
            showITUZonesError('Ошибка при загрузке данных зон: ' + error.message);
        }
    }

    // Рендеринг таблицы зон ITU
    function renderLotwITUZonesTable(ratings, totalZones, filters) {
        const contentDiv = document.getElementById('lotwITUZonesContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего зон:</strong> ${totalZones}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Зон</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-zones='${JSON.stringify(item.zones).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupITUZoneDetailButtons();
    }

    // Настройка кнопок для показа деталей по зонам
    function setupITUZoneDetailButtons() {
        const buttons = document.querySelectorAll('#lotwITUZonesContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const zones = JSON.parse(this.getAttribute('data-zones'));
                showITUZoneDetailModal(callsign, zones);
            });
        });
    }

    // Показ модального окна с деталями по зонам для позывного
    function showITUZoneDetailModal(callsign, zones) {
        let modal = document.getElementById('lotwITUZoneDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwITUZoneDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Зоны ITU
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего зон: <strong>${zones.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 80px;">Зона</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${zones.map((zone, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${zone.code}</span>
                                                    </td>
                                                    <td>
                                                        ${zone.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwITUZoneDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Зоны ITU`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего зон: <strong>${zones.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 80px;">Зона</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${zones.map((zone, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${zone.code}</span>
                                    </td>
                                    <td>
                                        ${zone.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для зон ITU
    function showITUZonesError(message) {
        const contentDiv = document.getElementById('lotwITUZonesContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно зон ITU
    initLotwITUZonesModal();

    // Инициализация модального окна IOTA
    function initLotwIOTAModal() {
        const modal = document.getElementById('lotwIOTAModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwIOTAData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных IOTA с учетом фильтров
    async function loadLotwIOTAData() {
        const contentDiv = document.getElementById('lotwIOTAContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных IOTA...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/iota/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwIOTATable(data.ratings, data.total_iotas, data.filters);
            } else {
                showIOTAError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw iota:', error);
            showIOTAError('Ошибка при загрузке данных IOTA: ' + error.message);
        }
    }

    // Рендеринг таблицы IOTA
    function renderLotwIOTATable(ratings, totalIotas, filters) {
        const contentDiv = document.getElementById('lotwIOTAContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего IOTA:</strong> ${totalIotas}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">IOTA</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-iotas='${JSON.stringify(item.iotas).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupIOTADetailButtons();
    }

    // Настройка кнопок для показа деталей по IOTA
    function setupIOTADetailButtons() {
        const buttons = document.querySelectorAll('#lotwIOTAContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const iotas = JSON.parse(this.getAttribute('data-iotas'));
                showIOTADetailModal(callsign, iotas);
            });
        });
    }

    // Показ модального окна с деталями по IOTA для позывного
    function showIOTADetailModal(callsign, iotas) {
        let modal = document.getElementById('lotwIOTADetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwIOTADetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - IOTA
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего IOTA: <strong>${iotas.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 100px;">IOTA</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${iotas.map((iota, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${iota.code}</span>
                                                    </td>
                                                    <td>
                                                        ${iota.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwIOTADetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - IOTA`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего IOTA: <strong>${iotas.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 100px;">IOTA</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${iotas.map((iota, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${iota.code}</span>
                                    </td>
                                    <td>
                                        ${iota.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для IOTA
    function showIOTAError(message) {
        const contentDiv = document.getElementById('lotwIOTAContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно IOTA
    initLotwIOTAModal();

    // Инициализация модального окна стран Р-150-С
    function initLotwR150sModal() {
        const modal = document.getElementById('lotwR150sModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwR150sData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных стран Р-150-С с учетом фильтров
    async function loadLotwR150sData() {
        const contentDiv = document.getElementById('lotwR150sContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных стран...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/r150s/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwR150sTable(data.ratings, data.total_countries, data.filters);
            } else {
                showR150sError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw r150s:', error);
            showR150sError('Ошибка при загрузке данных стран: ' + error.message);
        }
    }

    // Рендеринг таблицы стран Р-150-С
    function renderLotwR150sTable(ratings, totalCountries, filters) {
        const contentDiv = document.getElementById('lotwR150sContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего стран:</strong> ${totalCountries}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Стран</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-countries='${JSON.stringify(item.countries).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupR150sDetailButtons();
    }

    // Настройка кнопок для показа деталей по странам
    function setupR150sDetailButtons() {
        const buttons = document.querySelectorAll('#lotwR150sContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const countries = JSON.parse(this.getAttribute('data-countries'));
                showR150sDetailModal(callsign, countries);
            });
        });
    }

    // Показ модального окна с деталями по странам для позывного
    function showR150sDetailModal(callsign, countries) {
        let modal = document.getElementById('lotwR150sDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwR150sDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Страны Р-150-С
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего стран: <strong>${countries.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 200px;">Страна</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${countries.map((country, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${country.code}</span>
                                                    </td>
                                                    <td>
                                                        ${country.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwR150sDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Страны Р-150-С`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего стран: <strong>${countries.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 200px;">Страна</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${countries.map((country, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${country.code}</span>
                                    </td>
                                    <td>
                                        ${country.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для стран Р-150-С
    function showR150sError(message) {
        const contentDiv = document.getElementById('lotwR150sContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно стран Р-150-С
    initLotwR150sModal();

    // Инициализация модального окна стран DXCC
    function initLotwDXCCModal() {
        const modal = document.getElementById('lotwDXCCModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwDXCCData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных стран DXCC с учетом фильтров
    async function loadLotwDXCCData() {
        const contentDiv = document.getElementById('lotwDXCCContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных стран...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/dxcc/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwDXCCTable(data.ratings, data.total_countries, data.filters);
            } else {
                showDXCCError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw dxcc:', error);
            showDXCCError('Ошибка при загрузке данных стран: ' + error.message);
        }
    }

    // Рендеринг таблицы стран DXCC
    function renderLotwDXCCTable(ratings, totalCountries, filters) {
        const contentDiv = document.getElementById('lotwDXCCContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего стран:</strong> ${totalCountries}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Стран</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-countries='${JSON.stringify(item.countries).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupDXCCDetailButtons();
    }

    // Настройка кнопок для показа деталей по странам
    function setupDXCCDetailButtons() {
        const buttons = document.querySelectorAll('#lotwDXCCContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const countries = JSON.parse(this.getAttribute('data-countries'));
                showDXCCDetailModal(callsign, countries);
            });
        });
    }

    // Показ модального окна с деталями по странам для позывного
    function showDXCCDetailModal(callsign, countries) {
        let modal = document.getElementById('lotwDXCCDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwDXCCDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - Страны DXCC
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего стран: <strong>${countries.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 200px;">Страна</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${countries.map((country, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${country.code}</span>
                                                    </td>
                                                    <td>
                                                        ${country.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwDXCCDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - Страны DXCC`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего стран: <strong>${countries.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 200px;">Страна</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${countries.map((country, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${country.code}</span>
                                    </td>
                                    <td>
                                        ${country.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для стран DXCC
    function showDXCCError(message) {
        const contentDiv = document.getElementById('lotwDXCCContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно стран DXCC
    initLotwDXCCModal();

    // Инициализация модального окна QTH локаторов
    function initLotwQTHLocatorsModal() {
        const modal = document.getElementById('lotwQTHLocatorsModal');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function() {
            loadLotwQTHLocatorsData();
        });

        // Исправление проблемы с закрытием модального окна при скролле
        modal.addEventListener('hidden.bs.modal', function() {
            const otherModals = document.querySelectorAll('.modal.show');
            if (otherModals.length === 0) {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());

                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }

            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(m => m.classList.remove('show'));
        });
    }

    // Загрузка данных QTH локаторов с учетом фильтров
    async function loadLotwQTHLocatorsData() {
        const contentDiv = document.getElementById('lotwQTHLocatorsContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загрузка данных локаторов...</p>
            </div>
        `;

        try {
            const filterForm = document.querySelector('.filter-controls');
            const myCallsign = filterForm?.querySelector('[name="my_callsign"]')?.value || '';
            const searchCallsign = filterForm?.querySelector('[name="search_callsign"]')?.value || '';
            const searchQth = filterForm?.querySelector('[name="search_qth"]')?.value || '';
            const band = filterForm?.querySelector('[name="band"]')?.value || '';
            const mode = filterForm?.querySelector('[name="mode"]')?.value || '';
            const satName = filterForm?.querySelector('[name="sat_name"]')?.value || '';

            const params = new URLSearchParams({
                my_callsign: myCallsign,
                search_callsign: searchCallsign,
                search_qth: searchQth,
                band: band,
                mode: mode,
                sat_name: satName
            });

            const response = await fetch(`/api/lotw/qth-locators/?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                renderLotwQTHLocatorsTable(data.ratings, data.total_locators, data.filters);
            } else {
                showQTHLocatorsError('Ошибка при загрузке данных: ' + (data.error || 'Неизвестная ошибка'));
            }
        } catch (error) {
            console.error('Error loading lotw qth locators:', error);
            showQTHLocatorsError('Ошибка при загрузке данных локаторов: ' + error.message);
        }
    }

    // Рендеринг таблицы QTH локаторов
    function renderLotwQTHLocatorsTable(ratings, totalLocators, filters) {
        const contentDiv = document.getElementById('lotwQTHLocatorsContent');
        if (!contentDiv) return;

        if (!ratings || ratings.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-5">
                    <span class="display-4 text-muted">📭</span>
                    <h5 class="mt-3 text-muted">Нет данных для отображения</h5>
                    <p class="text-muted">Попробуйте изменить фильтры или добавьте новые QSO</p>
                </div>
            `;
            return;
        }

        let filterInfo = '';
        const activeFilters = [];
        if (filters.my_callsign) activeFilters.push(`Позывной: ${filters.my_callsign}`);
        if (filters.search_callsign) activeFilters.push(`Корреспондент: ${filters.search_callsign}`);
        if (filters.search_qth) activeFilters.push(`Локатор: ${filters.search_qth}`);
        if (filters.band) activeFilters.push(`Диапазон: ${filters.band}`);
        if (filters.mode) activeFilters.push(`Модуляция: ${filters.mode}`);
        if (filters.sat_name) activeFilters.push(`Спутник: ${filters.sat_name}`);

        if (activeFilters.length > 0) {
            filterInfo = `
                <div class="alert alert-info mb-3">
                    <strong>Активные фильтры:</strong> ${activeFilters.join(', ')}
                </div>
            `;
        }

        let html = `
            ${filterInfo}
            <div class="alert alert-success mb-3">
                <strong>Всего локаторов:</strong> ${totalLocators}
            </div>
            <div class="table-responsive">
                <table class="table table-hover table-striped lotw-regions-table">
                    <thead>
                        <tr>
                            <th class="col-num">№</th>
                            <th>Позывной</th>
                            <th class="col-regions-count">Локаторов</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        ratings.forEach((item, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><span class="callsign-badge">${item.callsign}</span></td>
                    <td class="col-regions-count">
                        <button type="button" class="btn btn-link count-link p-0 fw-bold"
                                data-callsign="${item.callsign}"
                                data-locators='${JSON.stringify(item.locators).replace(/'/g, "&#39;")}'>
                            ${item.count}
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

        setupQTHLocatorsDetailButtons();
    }

    // Настройка кнопок для показа деталей по локаторам
    function setupQTHLocatorsDetailButtons() {
        const buttons = document.querySelectorAll('#lotwQTHLocatorsContent .count-link');
        buttons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.stopPropagation();
                event.preventDefault();

                const callsign = this.getAttribute('data-callsign');
                const locators = JSON.parse(this.getAttribute('data-locators'));
                showQTHLocatorsDetailModal(callsign, locators);
            });
        });
    }

    // Показ модального окна с деталями по локаторам для позывного
    function showQTHLocatorsDetailModal(callsign, locators) {
        let modal = document.getElementById('lotwQTHLocatorsDetailModal');
        if (!modal) {
            const modalHtml = `
                <div class="modal fade lotw-regions-modal" id="lotwQTHLocatorsDetailModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title">
                                    <span class="callsign-badge">${callsign}</span> - QTH локаторы
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">Всего локаторов: <strong>${locators.length}</strong></p>
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped lotw-regions-table">
                                        <thead>
                                            <tr>
                                                <th style="width: 60px;">№</th>
                                                <th style="width: 100px;">Локатор</th>
                                                <th>Позывные</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${locators.map((locator, index) => `
                                                <tr>
                                                    <td>${index + 1}</td>
                                                    <td>
                                                        <span class="badge bg-secondary">${locator.code}</span>
                                                    </td>
                                                    <td>
                                                        ${locator.callsigns.map(call => `
                                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                                        `).join('')}
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            modal = document.getElementById('lotwQTHLocatorsDetailModal');
        } else {
            const modalTitle = modal.querySelector('.modal-title');
            const modalBody = modal.querySelector('.modal-body');

            modalTitle.innerHTML = `<span class="callsign-badge">${callsign}</span> - QTH локаторы`;
            modalBody.innerHTML = `
                <p class="text-muted mb-3">Всего локаторов: <strong>${locators.length}</strong></p>
                <div class="table-responsive">
                    <table class="table table-hover table-striped lotw-regions-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">№</th>
                                <th style="width: 100px;">Локатор</th>
                                <th>Позывные</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${locators.map((locator, index) => `
                                <tr>
                                    <td>${index + 1}</td>
                                    <td>
                                        <span class="badge bg-secondary">${locator.code}</span>
                                    </td>
                                    <td>
                                        ${locator.callsigns.map(call => `
                                            <span class="badge region-callsign-badge me-1">${call}</span>
                                        `).join('')}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Показ ошибки для QTH локаторов
    function showQTHLocatorsError(message) {
        const contentDiv = document.getElementById('lotwQTHLocatorsContent');
        if (!contentDiv) return;

        contentDiv.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <strong>Ошибка:</strong> ${message}
            </div>
        `;
    }

    // Инициализируем модальное окно QTH локаторов
    initLotwQTHLocatorsModal();

});