/**
 * Компактный JavaScript для страницы редактирования профиля
 * 
 * ВАЖНО: Поля LoTW НЕ обязательны для сохранения формы
 * - Основная информация и позывные сохраняются всегда
 * - LoTW данные сохраняются только если заполнены
 * - Валидация LoTW не блокирует отправку формы
 * 
 * Функции:
 * - Добавление/удаление позывных для LoTW
 * - Проверка учетных данных LoTW
 * - Валидация форм (без блокировки LoTW)
 * - Улучшенный UX с анимациями
 */

// Глобальные переменные
let callsignsData = [];
let isInitialized = false;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Инициализация компактной страницы профиля...');
    
    if (isInitialized) return;
    isInitialized = true;
    
    try {
        initializeProfile();
        initializeLoTW();
        updateFormValidation();
        
        console.log('✅ Компактная страница профиля успешно инициализирована');
    } catch (error) {
        console.error('❌ Ошибка инициализации:', error);
    }
});

// ========== ОСНОВНАЯ ИНИЦИАЛИЗАЦИЯ ==========

function initializeProfile() {
    loadCallsignsFromDatabase();
    renderCallsignsInUI();
    updateCallsignsData();
    
    // Сразу убираем блокировки с полей LoTW при инициализации
    updateFormValidation();
    
    // Показываем информационное сообщение пользователю
    setTimeout(() => {
        showNotification('💡 LoTW поля не обязательны - основная информация сохранится в любом случае', 'info');
    }, 500);
    
    // Отладочная информация о полях формы
    console.log('📋 Отладочная информация о полях формы:');
    const firstNameField = document.querySelector('input[name="first_name"]');
    const lastNameField = document.querySelector('input[name="last_name"]');
    const emailField = document.querySelector('input[name="email"]');
    
    if (firstNameField) console.log(`   first_name: "${firstNameField.value}"`);
    if (lastNameField) console.log(`   last_name: "${lastNameField.value}"`);
    if (emailField) console.log(`   email: "${emailField.value}"`);
    
    // Проверяем, есть ли сообщения об ошибке LoTW и сохраняем вкладку открытой
    checkLoTWErrorMessages();
    
    // Периодически проверяем сообщения для обновления статуса
    setInterval(checkLoTWErrorMessages, 1000);
}
        
// Проверяем наличие сообщений об ошибке LoTW и сохраняем вкладку открытой
function checkLoTWErrorMessages() {
    const alerts = document.querySelectorAll('.alert');
    let hasLoTWError = false;
    let hasLoTWSuccess = false;
    let errorMessage = '';
    let successMessage = '';
    
    alerts.forEach(alert => {
        const text = alert.textContent.toLowerCase();
        if (text.includes('lotw') || text.includes('логин') || text.includes('пароль')) {
            if (alert.classList.contains('alert-success')) {
                hasLoTWSuccess = true;
                successMessage = alert.textContent.trim();
                console.log('✅ Обнаружено успешное сообщение LoTW:', successMessage);
            } else if (alert.classList.contains('alert-danger') || alert.classList.contains('alert-error')) {
                hasLoTWError = true;
                errorMessage = alert.textContent.trim();
                console.log('❌ Обнаружена ошибка LoTW:', errorMessage);
            }
        }
    });
    
    // Если есть успешное сообщение LoTW, обновляем статус на успех
    if (hasLoTWSuccess) {
        console.log('🔧 Обновляем статус LoTW на успех');
        updateLoTWStatus('success', 'LoTW настроен и проверен');
        return;
    }

    // Если есть ошибка LoTW, обновляем статус
    if (hasLoTWError) {
        console.log('🔧 Обновляем статус LoTW из-за ошибки');
        updateLoTWStatus('error', errorMessage);
    }
}
        
// Обновляем статус LoTW в интерфейсе
function updateLoTWStatus(type, message) {
    const statusContainer = document.getElementById('lotw_status_container');
    if (!statusContainer) return;
    
    // Находим существующий статусный элемент
    const statusItems = statusContainer.querySelectorAll('.status-item');
    
    // Удаляем существующие статусы
    statusItems.forEach(item => item.remove());
    
    // Создаем новый статус
    const newStatus = document.createElement('div');
    newStatus.className = `status-item ${type}`;
    
    if (type === 'error') {
        newStatus.innerHTML = `<span>❌</span> ${message}`;
    } else if (type === 'success') {
        newStatus.innerHTML = `<span>✅</span> ${message}`;
    } else if (type === 'warning') {
        newStatus.innerHTML = `<span>⚠️</span> ${message}`;
    } else {
        newStatus.innerHTML = `<span>ℹ️</span> ${message}`;
    }
    
    // Вставляем новый статус перед sync-info
    const syncInfo = statusContainer.querySelector('.sync-info');
    if (syncInfo) {
        statusContainer.insertBefore(newStatus, syncInfo);
    } else {
        statusContainer.appendChild(newStatus);
    }
    
    console.log(`🔄 Обновлен статус LoTW: ${type} - ${message}`);
}
        
function loadCallsignsFromDatabase() {
    const jsonField = document.getElementById('my_callsigns_json');
    if (!jsonField) {
        console.warn('⚠️ Поле для позывных не найдено');
        callsignsData = [];
        return;
    }
    
    try {
        const rawData = jsonField.value.trim();
        console.log('📡 Загружаем данные позывных:', rawData);
        
        if (!rawData || rawData === '[]') {
            console.log('ℹ️ Позывные отсутствуют, начинаем с пустого списка');
            callsignsData = [];
            return;
        }
        
        // Парсим JSON
        const parsedData = JSON.parse(rawData);
        
        // Нормализуем данные (приводим к верхнему регистру)
        if (Array.isArray(parsedData)) {
            callsignsData = parsedData.map(callsign => {
                if (typeof callsign === 'string') {
                    return callsign.toUpperCase().trim();
                } else if (callsign && typeof callsign === 'object' && callsign.name) {
                    return callsign.name.toUpperCase().trim();
                }
                return '';
            }).filter(callsign => callsign && callsign.length > 0);
        } else {
            console.warn('⚠️ Неверный формат данных позывных');
            callsignsData = [];
        }
        
        console.log('✅ Позывные загружены:', callsignsData);
        
    } catch (error) {
        console.error('❌ Ошибка загрузки позывных:', error);
        callsignsData = [];
    }
}

function renderCallsignsInUI() {
    const container = document.getElementById('callsigns-container');
    if (!container) {
        console.error('❌ Контейнер для позывных не найден');
        return;
    }
    
    // Очищаем контейнер
    container.innerHTML = '';
    
    // Если есть позывные, отображаем их
    if (callsignsData.length > 0) {
        callsignsData.forEach(callsign => {
            addCallsignToUI(callsign);
        });
    }
    // Если позывных нет, оставляем контейнер пустым (пользователь сам добавит)
}

// ========== УПРАВЛЕНИЕ ПОЗЫВНЫМИ ==========

function addCallsign() {
    console.log('➕ Добавляем новый позывной');
    
    const container = document.getElementById('callsigns-container');
    if (!container) {
        console.error('❌ Контейнер для позывных не найден');
        return;
    }

    // Создаем новый элемент
    const item = createCallsignItem('');
    container.appendChild(item);
    
    // Фокусируемся на новом поле
    const input = item.querySelector('.callsign-input');
    input.focus();
    
    // Анимация появления
    item.style.opacity = '0';
    item.style.transform = 'translateY(15px)';
    setTimeout(() => {
        item.style.transition = 'all 0.3s ease';
        item.style.opacity = '1';
        item.style.transform = 'translateY(0)';
    }, 10);
    
    updateCallsignsData();
    console.log('✅ Позывной добавлен');
}

function addCallsignToUI(callsignValue) {
    const container = document.getElementById('callsigns-container');
    if (!container) return;
    
    const item = createCallsignItem(callsignValue);
    container.appendChild(item);
    
    return item;
}

// ==== Новая реализация функции createCallsignItem ====
function createCallsignItem(callsignValue) {
    const item = document.createElement('div');
    item.className = 'callsign-item';
    item.innerHTML = `
        <input type="text" class="form-control callsign-input"
               name="my_callsigns_names[]"
               value="${callsignValue || ''}"
               placeholder="Позывной (латинские буквы, цифры, /) - можно строчные"
               autocomplete="off"
               maxlength="20">
        <button type="button" class="btn remove-callsign-btn"
                onclick="removeCallsign(this)" title="Удалить позывной">
            ✖
        </button>
    `;

    // Инициализируем обработчики
    const input = item.querySelector('.callsign-input');
    initializeCallsignInput(input);
    
    return item;
}
// ==== Конец новой реализации ====

function removeCallsign(button) {
    console.log('🗑️ Удаляем позывной');
    
    const item = button.closest('.callsign-item');
    if (item) {
        // Анимация удаления
        item.style.transition = 'all 0.3s ease';
        item.style.opacity = '0';
        item.style.transform = 'translateX(15px)';
        
        setTimeout(() => {
            item.remove();
            updateCallsignsData();
            console.log('✅ Позывной удален');
        }, 250);
    }
}

function initializeCallsignInput(input) {
    if (!input) return;
    
    // Автоматическое преобразование в верхний регистр
    input.addEventListener('input', function() {
        const oldLength = this.value.length;
        
        // Разрешаем строчные и заглавные латинские буквы, цифры и слеш
        // Применяем фильтрацию и приводим к верхнему регистру
        this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
        
        // Устанавливаем курсор в конец строки для корректного набора
        this.setSelectionRange(this.value.length, this.value.length);
        
        updateCallsignsData();
    });
    
    // Очистка при потере фокуса
    input.addEventListener('blur', function() {
        this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
        clearValidationMessage(this);
        updateCallsignsData();
    });
    
    // Обработка вставки текста (Ctrl+V и через меню)
    input.addEventListener('paste', function() {
        // Даем браузеру вставить текст, а потом обрабатываем
        setTimeout(() => {
            const oldLength = this.value.length;
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
            this.setSelectionRange(this.value.length, this.value.length);
            updateCallsignsData();
        }, 0);
    });
    
    // Разрешенные символы при вводе (включая строчные буквы)
    input.addEventListener('keypress', function(e) {
        const char = String.fromCharCode(e.which);
        
        // Разрешаем backspace, delete, tab, escape, enter
        if ([46, 8, 9, 27, 13, 110].indexOf(e.keyCode) !== -1 ||
            // Разрешаем Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
            (e.keyCode === 65 && e.ctrlKey === true) ||
            (e.keyCode === 67 && e.ctrlKey === true) ||
            (e.keyCode === 86 && e.ctrlKey === true) ||
            (e.keyCode === 88 && e.ctrlKey === true)) {
            return;
        }
        
        // Разрешаем латинские буквы (строчные и заглавные), цифры и слеш
        if (!/^[A-Za-z0-9\/]$/.test(char)) {
            e.preventDefault();
            return;
        }
    });
        
    // Обработка клавиши Enter для добавления нового поля
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addCallsign();
        }
    });
}

function validateCallsign(input) {
    // Убираем всю валидацию формата, оставляем только очистку ошибок
    clearValidationMessage(input);
    return true;
}

function showValidationMessage(input, message) {
    clearValidationMessage(input);
    
    input.setCustomValidity(message);
    input.style.borderColor = '#dc3545';
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    feedback.style.display = 'block';
    
    input.parentNode.appendChild(feedback);
}

function clearValidationMessage(input) {
    input.setCustomValidity('');
    input.style.borderColor = '';
    
    const feedback = input.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}
    
function updateCallsignsData() {
    const inputs = document.querySelectorAll('.callsign-input');
    callsignsData = [];
    
    inputs.forEach(input => {
        const value = input.value.trim().toUpperCase();
        if (value) {
            // Проверяем на дубликаты
            if (!callsignsData.includes(value)) {
                callsignsData.push(value);
            }
        }
    });
    
    // Сохраняем в скрытое поле
    const jsonField = document.getElementById('my_callsigns_json');
    if (jsonField) {
        jsonField.value = JSON.stringify(callsignsData);
        console.log('💾 Обновлены данные позывных:', callsignsData);
    }
    
    return callsignsData;
}

// ========== УПРАВЛЕНИЕ LOTW ==========

function initializeLoTW() {
    // Валидация полей LoTW (без чекбокса активации)
    const lotwInputs = document.querySelectorAll('input[name="lotw_user"], input[name="lotw_password"]');
    lotwInputs.forEach(input => {
        input.addEventListener('input', updateLoTWValidation);
        input.addEventListener('blur', updateLoTWValidation);
    });
    
    // Сразу настраиваем поля как необязательные
    updateLoTWValidation();
    
    console.log('🌐 LoTW инициализирован - поля не обязательны');
}

// ==== Новая реализация функции updateLoTWValidation ====
function updateLoTWValidation() {
    const lotwUserInput = document.querySelector('input[name="lotw_user"]');
    const lotwPasswordInput = document.querySelector('input[name="lotw_password"]');
    
    // Поля LoTW НЕ обязательны - убираем required и блокировки
    if (lotwUserInput) {
        lotwUserInput.required = false;
        lotwUserInput.setCustomValidity(''); // Убираем блокировки
        clearValidationMessage(lotwUserInput);
        lotwUserInput.addEventListener('input', validateLoTWUser);
    }
    if (lotwPasswordInput) {
        lotwPasswordInput.required = false;
        lotwPasswordInput.setCustomValidity(''); // Убираем блокировки
        clearValidationMessage(lotwPasswordInput);
    }
    
    console.log('🔓 LoTW поля освобождены от обязательности');
}
// ==== Конец новой реализации ====

function validateLoTWUser() {
    const input = document.querySelector('input[name="lotw_user"]');
    if (!input) return;
    
    const callsign = input.value.trim();
    
    // Если поле пустое - не показываем ошибку (поле не обязательно)
    if (!callsign) {
        clearValidationMessage(input);
        input.setCustomValidity(''); // Убираем любые блокировки
        return true;
    }
    
    // Если есть значение - проверяем только разрешенные символы (включая строчные буквы)
    const allowedPattern = /^[A-Za-z0-9\/]*$/;
    if (!allowedPattern.test(callsign)) {
        // Для LoTW полей НЕ блокируем отправку формы - только визуальная подсказка
        input.setCustomValidity(''); // Убираем блокировку
        input.style.borderColor = '#dc3545';
        
        // Показываем подсказку без блокировки
        clearValidationMessage(input);
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = 'Используйте только латинские буквы, цифры и символ /';
        feedback.style.display = 'block';
        input.parentNode.appendChild(feedback);
        
        return false;
    }
    
    clearValidationMessage(input);
    input.setCustomValidity(''); // Убираем любые блокировки
    return true;
}

// ==== Новая реализация функции verifyLotwCredentials ====
window.verifyLotwCredentials = function() {
    console.log('🔍 Проверяем учетные данные LoTW...');
    
    const lotwUser = document.querySelector('input[name="lotw_user"]')?.value.trim();
    const lotwPassword = document.querySelector('input[name="lotw_password"]')?.value.trim();
    
    if (!lotwUser || !lotwPassword) {
        showNotification('⚠️ Пожалуйста, введите логин и пароль LoTW', 'warning');
        return;
    }

    // Разрешаем строчные и заглавные латинские буквы
    const allowedPattern = /^[A-Za-z0-9\/]*$/;
    if (!allowedPattern.test(lotwUser)) {
        showNotification('❌ Используйте только латинские буквы, цифры и символ /', 'error');
        return;
    }
    
    // Показываем индикатор загрузки
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<span>⏳</span> Проверяем...';
    button.disabled = true;

    // Создаем отдельную форму для проверки LoTW (не влияет на основную форму)
    const form = createCSRFProtectedForm('/profile/verify-lotw/');
    
    const userInput = document.createElement('input');
    userInput.type = 'hidden';
    userInput.name = 'lotw_user';
    userInput.value = lotwUser;
    form.appendChild(userInput);

    const passwordInput = document.createElement('input');
    passwordInput.type = 'hidden';
    passwordInput.name = 'lotw_password';
    passwordInput.value = lotwPassword;
    form.appendChild(passwordInput);

    document.body.appendChild(form);
    form.submit();
    
    // НЕ восстанавливаем кнопку автоматически - пусть пользователь сам решает
    // Кнопка восстановится после перезагрузки страницы
};
// ==== Конец новой реализации ====

window.deleteLotwCredentials = function() {
    if (confirm('🗑️ Вы уверены, что хотите удалить сохраненные логин и пароль LoTW?')) {
        console.log('🗑️ Удаляем учетные данные LoTW');
        
        const form = createCSRFProtectedForm('/profile/delete-lotw/');
        document.body.appendChild(form);
        form.submit();
    }
};

// ========== ВАЛИДАЦИЯ ФОРМЫ ==========

// Updated function to reflect new validation logic
function initializeFormValidation() {
    const profileForm = document.getElementById('profile-edit-form');
    if (profileForm) {
        // НЕ блокируем отправку формы - позволяем сохранить основную информацию
        profileForm.addEventListener('submit', function(event) {
            console.log('📝 Отправка формы профиля (LoTW поля не обязательны)');
            
            // Обновляем данные позывных
            updateCallsignsData();
            
            // Очищаем любые блокировки от валидации LoTW
            const lotwUserInput = document.querySelector('input[name="lotw_user"]');
            const lotwPasswordInput = document.querySelector('input[name="lotw_password"]');
            
            if (lotwUserInput) {
                lotwUserInput.setCustomValidity('');
                clearValidationMessage(lotwUserInput);
                lotwUserInput.required = false; // Гарантируем, что поле не обязательно
            }
            if (lotwPasswordInput) {
                lotwPasswordInput.setCustomValidity('');
                clearValidationMessage(lotwPasswordInput);
                lotwPasswordInput.required = false; // Гарантируем, что поле не обязательно
            }
            
            // Форма отправляется без блокировок
            console.log('✅ Форма готова к отправке - сохранение возможно без LoTW данных');
            
            // Показываем уведомление пользователю
            setTimeout(() => {
                showNotification('💾 Форма отправляется. Основная информация и позывные будут сохранены.', 'info');
            }, 100);
        });
    }
}

// ========== ГЛОБАЛЬНЫЕ ФУНКЦИИ ==========

// Делаем функции глобально доступными для onclick атрибутов
window.addCallsign = addCallsign;
window.removeCallsign = removeCallsign;
window.verifyLotwCredentials = verifyLotwCredentials;
window.deleteLotwCredentials = deleteLotwCredentials;

// Вспомогательные функции
function createCSRFProtectedForm(action) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = action;
    form.style.display = 'none';

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
    }

    return form;
}

function showNotification(message, type = 'info') {
    // Создаем уведомление
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    
    const icon = type === 'success' ? '✅' : 
                 type === 'error' ? '❌' : 
                 type === 'warning' ? '⚠️' : 'ℹ️';
    
    alertDiv.innerHTML = `
        <span>${icon}</span> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Вставляем в начало формы
    const form = document.getElementById('profile-edit-form');
    if (form) {
        form.insertBefore(alertDiv, form.firstChild);
        
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Экспорт для отладки
window.ProfileEditor = {
    callsignsData,
    addCallsign,
    removeCallsign,
    updateCallsignsData,
    validateCallsign,
    showNotification
};

console.log('🚀 Компактный скрипт страницы профиля загружен');