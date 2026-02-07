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
    
    // Инициализируем валидацию формы с проверкой LoTW + позывные
    initializeFormValidation();
    
    // Инициализируем состояние пароля LoTW
    initializePasswordToggle();
    
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
    
    console.log(`📡 Найдено ${inputs.length} полей позывных`);
    
    inputs.forEach((input, index) => {
        const value = input.value.trim().toUpperCase();
        console.log(`   Поле ${index}: "${value}"`);
        if (value) {
            // Проверяем на дубликаты
            if (!callsignsData.includes(value)) {
                callsignsData.push(value);
                console.log(`   ✅ Добавлен: ${value}`);
            } else {
                console.log(`   ⚠️ Дубликат пропущен: ${value}`);
            }
        }
    });
    
    // Сохраняем в скрытое поле
    const jsonField = document.getElementById('my_callsigns_json');
    if (jsonField) {
        const jsonValue = JSON.stringify(callsignsData);
        jsonField.value = jsonValue;
        console.log('💾 Обновлены данные позывных:', jsonValue);
    } else {
        console.error('❌ Скрытое поле my_callsigns_json не найдено!');
    }
    
    return callsignsData;
}

function initializeFormValidation() {
    const profileForm = document.getElementById('profile-edit-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(event) {
            console.log('📝 Отправка формы профиля');
            
            // ===== ПРОВЕРКА: Если это удаление LoTW - не блокируем =====
            if (event.submitter && event.submitter.onclick && 
                event.submitter.onclick.toString().includes('deleteLotwCredentials')) {
                console.log('✅ Обнаружено удаление LoTW - пропускаем валидацию');
                return; // Пропускаем валидацию для удаления LoTW
            }
            
            // ===== ВАЖНО: Принудительно обновляем данные позывных =====
            updateCallsignsData();
            
            // ===== НОВАЯ ВАЛИДАЦИЯ: Проверка LoTW с позывными =====
            const lotwVerified = document.getElementById('lotw_verified')?.value === 'true';
            const hasCallsigns = callsignsData.length > 0;
            
            console.log(`🔍 Проверка валидации LoTW:`);
            console.log(`   lotw_verified: ${lotwVerified}`);
            console.log(`   callsigns_count: ${callsignsData.length}`);
            console.log(`   has_callsigns: ${hasCallsigns}`);
            
            // Если LoTW настроен (проверен), но нет позывных - блокируем отправку
            if (lotwVerified && !hasCallsigns) {
                event.preventDefault();
                
                // Показываем сообщение об ошибке
                showNotification('❌ Добавьте хотя бы один позывной синхронизации для LoTW', 'error');
                
                // Прокручиваем к секции позывных
                const callsignsSection = document.querySelector('.callsigns-container-compact');
                if (callsignsSection) {
                    callsignsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                console.log('❌ Отправка формы заблокирована: LoTW настроен без позывных');
                return false;
            }
            
            // Проверяем, что данные попали в скрытое поле
            const jsonField = document.getElementById('my_callsigns_json');
            if (jsonField) {
                console.log('📡 Данные позывных для отправки:', jsonField.value);
            }
            
            // Очищаем любые блокировки от валидации LoTW
            const lotwUserInput = document.querySelector('input[name="lotw_user"]');
            const lotwPasswordInput = document.querySelector('input[name="lotw_password"]');
            
            if (lotwUserInput) {
                lotwUserInput.setCustomValidity('');
                clearValidationMessage(lotwUserInput);
                lotwUserInput.required = false; // Гарантируем, что поле не обязано
            }
            if (lotwPasswordInput) {
                lotwPasswordInput.setCustomValidity('');
                clearValidationMessage(lotwPasswordInput);
                lotwPasswordInput.required = false; // Гарантируем, что поле не обязано
            }
            
            // Форма отправляется без блокировок (если прошла валидацию)
            console.log('✅ Форма готова к отправке');
            
            // Показываем уведомление пользователю
            setTimeout(() => {
                if (lotwVerified && hasCallsigns) {
                    showNotification('💾 Форма отправляется. LoTW и позывные настроены корректно.', 'success');
                } else {
                    showNotification('💾 Форма отправляется. Основная информация и позывные будут сохранены.', 'info');
                }
            }, 100);
        });
    }
}

// ========== ГЛОБАЛЬНЫЕ ФУНКЦИИ ==========

// Делаем функции глобально доступными для onclick атрибутов
window.addCallsign = addCallsign;
window.removeCallsign = removeCallsign;
window.verifyLotwCredentials = function() {
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
/**
 * Удаление учетных данных LoTW
 */
window.deleteLotwCredentials = function(event) {
    // Предотвращаем всплытие и默认行为
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    if (confirm('Вы уверены, что хотите удалить сохраненные логин и пароль LoTW?')) {
        console.log('🗑️ Удаление учетных данных LoTW');
        
        // Создаем форму для отправки данных удаления
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/profile/delete-lotw/';
        form.style.display = 'none';

        // Добавляем CSRF токен
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
        if (!csrfToken) {
            showNotification('❌ Ошибка: CSRF токен не найден', 'error');
            return;
        }

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);

        // Показываем индикатор загрузки
        showNotification('⏳ Удаление учетных данных LoTW...', 'info');

        document.body.appendChild(form);
        form.submit();
    }
};

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

// ========== ПЕРЕКЛЮЧЕНИЕ ВИДИМОСТИ ПАРОЛЯ ==========

/**
 * Переключает видимость пароля для поля с указанным ID
 * @param {string} fieldId - ID поля пароля
 * @param {HTMLElement} button - Кнопка переключения
 */
function togglePasswordVisibility(fieldId, button) {
    const passwordField = document.getElementById(fieldId);
    if (!passwordField || !button) {
        console.error('❌ Поле пароля или кнопка не найдены');
        return;
    }
    
    const toggleIcon = button.querySelector('.toggle-icon');
    
    if (passwordField.type === 'password') {
        // Показываем пароль
        passwordField.type = 'text';
        button.classList.remove('hidden');
        button.classList.add('visible');
        toggleIcon.textContent = '🙈';
        
        // Стилизуем кнопку как активную
        button.style.background = 'rgba(102, 126, 234, 0.1)';
        button.style.color = '#667eea';
        
        console.log('👁️ Пароль показан');
    } else {
        // Скрываем пароль
        passwordField.type = 'password';
        button.classList.remove('visible');
        button.classList.add('hidden');
        toggleIcon.textContent = '👁️';
        
        // Возвращаем кнопку к исходному состоянию
        button.style.background = 'transparent';
        button.style.color = '';
        
        console.log('🙈 Пароль скрыт');
    }
}

// Делаем функцию глобально доступной для onclick атрибутов
window.togglePasswordVisibility = togglePasswordVisibility;

/**
 * Инициализирует состояние переключателя пароля
 */
function initializePasswordToggle() {
    const passwordField = document.getElementById('lotw_password_field');
    const toggleButton = document.querySelector('.password-toggle');
    
    if (passwordField && toggleButton) {
        // Устанавливаем начальное состояние - пароль скрыт (type="password")
        toggleButton.classList.add('hidden');
        
        console.log('🔒 Переключатель пароля LoTW инициализирован');
    } else {
        console.warn('⚠️ Элементы переключения пароля не найдены');
    }
}

// Делаем функцию доступной глобально
window.initializePasswordToggle = initializePasswordToggle;

// Экспорт для отладки
window.ProfileEditor = {
    callsignsData,
    addCallsign,
    removeCallsign,
    updateCallsignsData,
    validateCallsign,
    showNotification,
    togglePasswordVisibility,
    initializePasswordToggle
};

console.log('🚀 Компактный скрипт страницы профиля загружен');
