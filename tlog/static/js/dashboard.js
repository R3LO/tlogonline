/* =====================================
   Dashboard JavaScript функциональность
   ===================================== */

// Инициализация dashboard при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
    initProfileSettings();
    initStatisticsAnimation();
});

/**
 * Основная инициализация dashboard
 */
function initDashboard() {
    // Анимация статистических карточек
    animateStatCards();
    
    // Обновление статистики в реальном времени
    setupRealtimeUpdates();
    
    // Инициализация графиков (если используются)
    initCharts();
}

/**
 * Анимация статистических карточек
 */
function animateStatCards() {
    const statCards = document.querySelectorAll('.dashboard-stat-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });
    
    statCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
}

/**
 * Настройки профиля
 */
function initProfileSettings() {
    const forms = document.querySelectorAll('.profile-settings-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', handleProfileUpdate);
    });
    
    // Автосохранение изменений в настройках
    const inputs = document.querySelectorAll('.auto-save');
    inputs.forEach(input => {
        input.addEventListener('change', autoSaveSettings);
    });
}

/**
 * Обработка обновления профиля
 */
function handleProfileUpdate(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Показываем состояние загрузки
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Сохранение...';
    submitButton.disabled = true;
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Настройки сохранены', 'success');
        } else {
            showNotification('Ошибка при сохранении: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка', 'error');
    })
    .finally(() => {
        // Восстанавливаем кнопку
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

/**
 * Автосохранение настроек
 */
function autoSaveSettings(event) {
    const input = event.target;
    const form = input.closest('form');
    
    if (form && form.dataset.autoSave === 'true') {
        clearTimeout(window.autoSaveTimeout);
        window.autoSaveTimeout = setTimeout(() => {
            const formData = new FormData(form);
            formData.append('auto_save', 'true');
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAutoSaveIndicator();
                }
            })
            .catch(error => {
                console.error('Ошибка автосохранения:', error);
            });
        }, 1000);
    }
}

/**
 * Показ индикатора автосохранения
 */
function showAutoSaveIndicator() {
    const indicator = document.getElementById('auto-save-indicator');
    if (indicator) {
        indicator.style.opacity = '1';
        setTimeout(() => {
            indicator.style.opacity = '0';
        }, 2000);
    }
}

/**
 * Обновление статистики в реальном времени
 */
function setupRealtimeUpdates() {
    // Обновляем статистику каждые 5 минут
    setInterval(updateStatistics, 300000);
}

/**
 * Обновление статистических данных
 */
function updateStatistics() {
    fetch('/dashboard/api/stats/')
    .then(response => response.json())
    .then(data => {
        updateStatValues(data);
    })
    .catch(error => {
        console.error('Ошибка обновления статистики:', error);
    });
}

/**
 * Обновление значений статистики с анимацией
 */
function updateStatValues(stats) {
    Object.keys(stats).forEach(key => {
        const element = document.getElementById(`stat-${key}`);
        if (element) {
            const currentValue = parseInt(element.textContent);
            const newValue = stats[key];
            
            if (currentValue !== newValue) {
                animateValue(element, currentValue, newValue, 1000);
            }
        }
    });
}

/**
 * Анимация изменения числовых значений
 */
function animateValue(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.round(start + (range * progress));
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

/**
 * Инициализация графиков (если используются библиотеки типа Chart.js)
 */
function initCharts() {
    const chartCanvas = document.getElementById('dashboard-chart');
    if (chartCanvas && typeof Chart !== 'undefined') {
        // Пример инициализации графика
        new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'],
                datasets: [{
                    label: 'QSO за месяц',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }
}

/**
 * Анимация загрузки статистики
 */
function initStatisticsAnimation() {
    const statNumbers = document.querySelectorAll('.dashboard-stat-value');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const finalValue = element.dataset.value || element.textContent;
                const numericValue = parseInt(finalValue.replace(/[^\d]/g, ''));
                
                if (numericValue) {
                    animateValue(element, 0, numericValue, 2000);
                }
                
                observer.unobserve(element);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(number => {
        observer.observe(number);
    });
}

/**
 * Утилита для получения CSRF токена
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

/**
 * Показ уведомлений
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}
