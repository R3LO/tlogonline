// Profile Edit JavaScript - ИСПРАВЛЕННАЯ ВЕРСИЯ
// ================================================

(function($) {
    'use strict';
    
    // console.log removed
    
    // ========== Инициализация при загрузке страницы ==========
    
    function initProfileEdit() {
        // console.log removed
        
        // Загружаем данные из базы в форму
        loadProfileData();
        
        // Инициализируем обработчики событий
        initEventHandlers();
        
        // Инициализируем поля ввода позывных
        initCallsignInputs();
    }
    
    // Загрузка данных профиля при загрузке страницы
    function loadProfileData() {
        // console.log removed
        
        const jsonField = document.getElementById('my_callsigns_json');
        if (!jsonField) {
            return;
        }
        
        const rawData = jsonField.value.trim();
        // console.log removed
        
        if (!rawData || rawData === '[]') {
            // console.log removed
            // Не добавляем поле автоматически - пользователь сам нажмет кнопку "Добавить позывной"
            return;
        }
        
        try {
            let callsigns;
            
            // Пытаемся распарсить как JSON
            try {
                callsigns = JSON.parse(rawData);
                // console.log removed
            } catch (parseError) {
                // console.log removed
                // Если не JSON, возможно это простой список строк
                if (rawData.startsWith('[') && rawData.endsWith(']')) {
                    // Это JSON, но с ошибкой парсинга
                    callsigns = [];
                } else {
                    // Это простой список строк
                    callsigns = rawData.split(',').map(s => s.trim()).filter(s => s);
                }
            }
            
            // Очищаем контейнер
            const container = document.getElementById('callsigns-container');
            container.innerHTML = '';
            
            // Добавляем позывные в форму
            if (Array.isArray(callsigns)) {
                if (callsigns.length > 0) {
                    callsigns.forEach(function(callsign) {
                        let callsignValue = '';
                        
                        if (typeof callsign === 'object' && callsign.name) {
                            callsignValue = callsign.name;
                        } else if (typeof callsign === 'string') {
                            callsignValue = callsign;
                        }
                        
                        addCallsign(callsignValue);
                    });
                    
                    // console.log removed
                } else {
                    // console.log removed
                    // Не добавляем пустое поле автоматически
                }
            } else {
                // Не добавляем пустое поле при ошибке
            }
            
        } catch (error) {
            // Не добавляем пустое поле при ошибке
        }
    }
    
    // ========== Callsign Management Functions ==========
    
    // Initialize handlers for existing callsign inputs
    function initCallsignInputs() {
        document.querySelectorAll('.callsign-input').forEach(input => {
            input.addEventListener('input', function() {
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
            });
        });
        // console.log removed
    }

    // Add new callsign input
    function addCallsign(value = '') {
        const container = document.getElementById('callsigns-container');
        const item = document.createElement('div');
        item.className = 'my-callsign-item mb-2 d-flex';
        item.innerHTML = `
            <input type="text" class="form-control name-input callsign-input flex-grow-1 me-2"
                   name="my_callsigns_names[]"
                   value="${value}"
                   placeholder="Позывной"
                   autocomplete="off">
            <button type="button" class="btn btn-outline-danger btn-sm"
                    onclick="removeCallsign(this)">
                ✕
            </button>
        `;
        container.appendChild(item);
        
        // Инициализируем обработчики для нового поля
        initCallsignInputs();
        
        // console.log removed
    }

    // Remove callsign input
    function removeCallsign(button) {
        const container = document.getElementById('callsigns-container');
        const items = container.querySelectorAll('.my-callsign-item');
        
        if (items.length > 1) {
            // Удаляем элемент
            const item = button.closest('.my-callsign-item');
            item.remove();
            // console.log removed
        } else {
            // Если это последний элемент, удаляем его полностью
            const item = button.closest('.my-callsign-item');
            item.remove();
            // console.log removed
        }
        
        // Если после удаления не осталось полей, ничего не добавляем автоматически
        // Пользователь сам может добавить поле кнопкой "Добавить позывной"
    }
    
    // ========== Event Handlers ==========
    
    function initEventHandlers() {
        const form = document.getElementById('profile-edit-form');
        if (!form) {
            return;
        }
        
        // Form submit handler
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // console.log removed
            // console.log removed
            
            const callsigns = [];
            const container = document.getElementById('callsigns-container');
            const items = container.querySelectorAll('.my-callsign-item');

            // console.log removed
            
            items.forEach(function(item, index) {
                const input = item.querySelector('input[name="my_callsigns_names[]"]');
                if (input) {
                    const name = input.value.trim();
                    // console.log removed
                    if (name) {
                        callsigns.push({
                            name: name.toUpperCase()
                        });
                    }
                }
            });

            // console.log removed
            
            const jsonField = document.getElementById('my_callsigns_json');
            if (jsonField) {
                const jsonValue = JSON.stringify(callsigns);
                jsonField.value = jsonValue;
                // console.log removed
                
                // Debug: проверим, что данные действительно попали в поле
                // console.log removed
            } else {
            }
            
            // Debug: проверим данные формы
            const formData = new FormData(form);
            
            // Показываем сообщение пользователю
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Сохранение...';
                submitBtn.disabled = true;
                
                // Восстанавливаем кнопку через 3 секунды
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
            
            return false; // Предотвращаем отправку формы для тестирования
        });
        
        // console.log removed
    }
    
    // ========== Global Functions ==========
    
    // Делаем функции глобально доступными для onclick атрибутов
    window.addCallsign = addCallsign;
    window.removeCallsign = removeCallsign;
    
    // ========== Initialize ==========
    
    // Инициализируем при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProfileEdit);
    } else {
        initProfileEdit();
    }
    
})(jQuery);
