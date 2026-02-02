// Базовые JavaScript функции для TLog проекта
document.addEventListener('DOMContentLoaded', function() {
    
    // Инициализация общих компонентов
    initCommonFeatures();
    initTooltips();
    initModals();
    initNotifications();
    
    // Общие функции
    function initCommonFeatures() {
        // Добавляем класс для анимаций загрузки
        document.body.classList.add('js-loaded');
        
        // Инициализация dropdown меню
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {
            new bootstrap.Dropdown(dropdown);
        });
        
        // Инициализация collapse элементов
        const collapses = document.querySelectorAll('.collapse');
        collapses.forEach(collapse => {
            new bootstrap.Collapse(collapse);
        });
    }
    
    // Инициализация tooltips
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Инициализация модальных окон
    function initModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            new bootstrap.Modal(modal);
        });
    }
    
    // Система уведомлений
    function initNotifications() {
        // Создаем контейнер для уведомлений если его нет
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'position-fixed';
            container.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
            document.body.appendChild(container);
        }
    }
    
    // Глобальные утилиты
    window.TLog = {
        // Показать уведомление
        showNotification: function(message, type = 'info', duration = 5000) {
            const container = document.getElementById('notification-container');
            if (!container) return;
            
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show mb-2`;
            notification.style.cssText = 'min-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
            
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            container.appendChild(notification);
            
            // Автоматически удаляем уведомление
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        },
        
        // Подтверждение действия
        confirmAction: function(message, callback) {
            if (confirm(message)) {
                callback();
            }
        },
        
        // AJAX запрос с обработкой ошибок
        ajax: function(url, options = {}) {
            return fetch(url, {
                headers: {
                    'X-CSRFToken': window.getCsrfToken(),
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                window.TLog.showNotification('Произошла ошибка при выполнении запроса', 'danger');
                throw error;
            });
        },
        
        // Форматирование даты
        formatDate: function(date, format = 'dd.mm.yyyy') {
            const d = new Date(date);
            const day = String(d.getDate()).padStart(2, '0');
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const year = d.getFullYear();
            
            return format
                .replace('dd', day)
                .replace('mm', month)
                .replace('yyyy', year);
        },
        
        // Валидация формы
        validateForm: function(formElement) {
            const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                }
            });
            
            return isValid;
        }
    };
    
    // Получение CSRF токена
    window.getCsrfToken = function() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    };
    
    // Обработка ошибок JavaScript
    window.addEventListener('error', function(e) {
        // В продакшене здесь можно отправлять ошибки на сервер
    });
    
    // Обработка ошибок Promise
    window.addEventListener('unhandledrejection', function(e) {
        // В продакшене здесь можно отправлять ошибки на сервер
    });
});

// Глобальные константы
window.TLogConstants = {
    ANIMATION_DURATION: 300,
    NOTIFICATION_DURATION: 5000,
    DEBOUNCE_DELAY: 300
};

// Функция debounce для оптимизации производительности
window.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Функция throttle для ограничения частоты вызовов
window.throttle = function(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};