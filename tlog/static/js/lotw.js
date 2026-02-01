// JavaScript для страницы LoTW с серверной фильтрацией
document.addEventListener('DOMContentLoaded', function() {
    
    // Инициализация всех функций
    initCardAnimations();
    initStatusRefresh();
    initQuickActions();
    initTooltips();
    initServerFilters();
    
    // Анимации для карточек
    function initCardAnimations() {
        const cards = document.querySelectorAll('.card');
        
        cards.forEach((card, index) => {
            // Добавляем задержку для каждой карточки
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }
            
    // Инициализация серверных фильтров
    function initServerFilters() {
        // Загружаем позывные пользователя
        loadUserCallsigns();
        
        // Никаких дополнительных обработчиков не нужно
        // Все работает через обычные HTML формы
        console.log('🔧 Серверные фильтры инициализированы');
    }
    
    // Загрузка позывных пользователя через серверный рендеринг
    function loadUserCallsigns() {
        // Позывные загружаются на сервере при рендеринге страницы
        // Никаких AJAX запросов не нужно
        console.log('📞 Позывные загружаются сервером при рендеринге');
    }

    // Функция очистки фильтров больше не нужна
    // Сброс выполняется через серверную форму
    
    // Функция инициализации пагинации (без AJAX)
    function initPagination() {
        // Пагинация работает через серверные формы
        // Никаких дополнительных обработчиков не нужно
        console.log('📄 Пагинация инициализирована (серверная)');
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
    
    
    // Экспортируем функции для глобального использования
    window.LoTW = {
        clearFilters: clearFilters,
        refreshStatus: refreshLoTWStatus,
        showNotification: showNotification,
        smoothScrollTo: smoothScrollTo
    };
});