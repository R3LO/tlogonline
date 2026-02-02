// JavaScript для страницы LoTW
document.addEventListener('DOMContentLoaded', function() {
    
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
                    ru_region: 'Московская область',
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
                ru_region: 'Московская область',
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
            'view_ru_region': qsoData.ru_region || '-',
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
    
});