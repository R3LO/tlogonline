// Упрощенная отладочная версия LoTW JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== LoTW DEBUG SCRIPT LOADED ===');
    
    // Создаем элемент для отладки на странице
    function createDebugInfo() {
        const debugDiv = document.createElement('div');
        debugDiv.id = 'lotw-debug-info';
        debugDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #f0f0f0;
            border: 2px solid #333;
            padding: 10px;
            z-index: 9999;
            font-family: monospace;
            font-size: 12px;
            max-width: 300px;
        `;
        debugDiv.innerHTML = '<h4>🔧 LoTW Debug</h4><div id="debug-content">Инициализация...</div>';
        document.body.appendChild(debugDiv);
        return debugDiv;
    }
    
    function updateDebug(message) {
        const debugContent = document.getElementById('debug-content');
        if (debugContent) {
            debugContent.innerHTML += `<div>${new Date().toLocaleTimeString()}: ${message}</div>`;
        }
        console.log('LoTW Debug:', message);
    }
    
    // Создаем информационную панель
    const debugPanel = createDebugInfo();
    updateDebug('Скрипт загружен');
    
    // Проверяем Bootstrap
    updateDebug(`Bootstrap доступен: ${typeof bootstrap !== 'undefined'}`);
    
    // Проверяем модальное окно
    const modal = document.getElementById('viewQSOModalLotw');
    updateDebug(`Модальное окно найдено: ${modal !== null}`);
    
    // Проверяем кнопки
    const buttons = document.querySelectorAll('.view-qso-btn');
    updateDebug(`Кнопки найдены: ${buttons.length}`);
    
    // Создаем тестовую кнопку
    function createTestButton() {
        const testBtn = document.createElement('button');
        testBtn.textContent = '🧪 Тест модального окна';
        testBtn.className = 'btn btn-danger btn-sm';
        testBtn.style.cssText = 'position: fixed; top: 10px; left: 10px; z-index: 9999;';
        testBtn.onclick = function() {
            updateDebug('Клик по тестовой кнопке');
            testModal();
        };
        document.body.appendChild(testBtn);
        updateDebug('Тестовая кнопка создана');
    }
    
    createTestButton();
    
    // Простая функция теста модального окна
    function testModal() {
        updateDebug('=== ТЕСТ МОДАЛЬНОГО ОКНА ===');
        
        if (!modal) {
            updateDebug('❌ Модальное окно не найдено!');
            alert('Модальное окно не найдено!');
            return;
        }
        
        if (typeof bootstrap === 'undefined') {
            updateDebug('❌ Bootstrap не загружен!');
            alert('Bootstrap не загружен!');
            return;
        }
        
        try {
            updateDebug('Заполняем тестовыми данными...');
            
            // Заполняем поля
            const testData = {
                'view_id': 'TEST_123',
                'view_callsign': 'TEST_CALL',
                'view_date': '2024-01-01',
                'view_time': '12:00',
                'view_band': '20m',
                'view_mode': 'SSB'
            };
            
            Object.keys(testData).forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.textContent = testData[fieldId];
                    updateDebug(`✅ Поле ${fieldId}: ${testData[fieldId]}`);
                } else {
                    updateDebug(`❌ Поле ${fieldId}: НЕ НАЙДЕНО`);
                }
            });
            
            updateDebug('Создаем модальное окно...');
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            updateDebug('✅ Модальное окно показано!');
            
        } catch (error) {
            updateDebug(`❌ Ошибка: ${error.message}`);
            alert('Ошибка: ' + error.message);
        }
    }
    
    // Обработчик кликов по кнопкам QSO
    document.addEventListener('click', function(event) {
        const button = event.target.closest('.view-qso-btn');
        if (button) {
            event.preventDefault();
            event.stopPropagation();
            
            const qsoId = button.getAttribute('data-qso-id');
            updateDebug(`Клик по QSO кнопке, ID: ${qsoId}`);
            
            if (qsoId) {
                // Используем упрощенную версию для показа модального окна
                testModal();
            }
            
            return false;
        }
    });
    
    // Добавляем глобальную функцию
    window.showQSOModal = testModal;
    updateDebug('Глобальная функция showQSOModal создана');
    
    // Финальная проверка
    updateDebug('=== ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА ===');
    updateDebug(`Функция showQSOModal: ${typeof window.showQSOModal}`);
    
    // Автоматический тест через 3 секунды
    setTimeout(() => {
        updateDebug('Автоматический тест через 3 секунды...');
        testModal();
    }, 3000);
});

// Дополнительная проверка загрузки скрипта
console.log('LoTW Debug Script: Скрипт загружен и выполнен');