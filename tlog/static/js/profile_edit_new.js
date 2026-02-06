/**
 * Улучшенный JavaScript для страницы редактирования профиля
 * Исправлены все проблемы с добавлением позывных и улучшен UX
 * 
 * Функции:
 * - Добавление/удаление позывных для LoTW
 * - Проверка учетных данных LoTW
 * - Смена пароля
 * - Валидация форм
 * - Улучшенный UX с анимациями
 */

// Глобальные переменные
let callsignsData = [];
let isInitialized = false;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Инициализация страницы профиля...');
    
    if (isInitialized) return;
    isInitialized = true;
    
    try {
        initializeProfile();
        initializeLoTW();
        initializePasswordChange();
        initializeFormValidation();
        
        console.log('✅ Страница профиля успешно инициализирована');
    } catch (error) {
        console.error('❌ Ошибка инициализации:', error);
    }
});

// ========== ОСНОВНАЯ ИНИЦИАЛИЗАЦИЯ ==========

function initializeProfile() {
    loadCallsignsFromDatabase();
    renderCallsignsInUI();
    updateCallsignsData();
    
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

    // Если есть ошибка LoTW, обновляем статус и показываем вкладку
    if (hasLoTWError) {
        console.log('🔧 Обновляем статус LoTW из-за ошибки');
        updateLoTWStatus('error', errorMessage);
        
        // Принудительно показываем вкладку
        const settings = document.getElementById('lotw_settings');
        const useLotwCheckbox = document.getElementById('use_lotw');
        const consentCheckbox = document.getElementById('lotw_consent');
        
        if (settings) {
            settings.style.display = 'block';
        }
        if (useLotwCheckbox) {
            useLotwCheckbox.checked = true;
        }
        if (consentCheckbox) {
            consentCheckbox.checked = true;
        }
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
        
        // Нормализуем данные
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
    item.style.transform = 'translateY(20px)';
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

function createCallsignItem(callsignValue) {
    const item = document.createElement('div');
    item.className = 'callsign-item';
    item.innerHTML = `
        <input type="text" class="form-control callsign-input"
               name="my_callsigns_names[]"
               value="${callsignValue || ''}"
               placeholder="Позывной (латинские буквы, цифры, /)"
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

function removeCallsign(button) {
    console.log('🗑️ Удаляем позывной');
    
    const item = button.closest('.callsign-item');
    if (item) {
        // Анимация удаления
        item.style.transition = 'all 0.3s ease';
        item.style.opacity = '0';
        item.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            item.remove();
            updateCallsignsData();
            console.log('✅ Позывной удален');
        }, 300);
    }
}

function initializeCallsignInput(input) {
    if (!input) return;
    
    // Автоматическое преобразование в верхний регистр
    input.addEventListener('input', function() {
        const oldLength = this.value.length;
        
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
    
    // Разрешенные символы при вводе
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
        
        // Разрешаем только латинские буквы, цифры и слеш
        if (!/^[A-Z0-9\/]$/.test(char)) {
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
    const useLotwCheckbox = document.getElementById('use_lotw');
    const consentCheckbox = document.getElementById('lotw_consent');
    
    if (useLotwCheckbox && consentCheckbox) {
        // Синхронизация чекбоксов с умной логикой
        useLotwCheckbox.addEventListener('change', function() {
            console.log('🔄 Изменение use_lotw чекбокса:', this.checked);
            
            // Синхронизируем согласие
            consentCheckbox.checked = this.checked;
            
            // Всегда вызываем toggleLotwSettings для обновления отображения
            toggleLotwSettings();
            updateLoTWValidation();
        });
        
        consentCheckbox.addEventListener('change', function() {
            console.log('🔄 Изменение consent чекбокса:', this.checked);
            
            // Синхронизируем основной чекбокс
            useLotwCheckbox.checked = this.checked;
            
            // Всегда вызываем toggleLotwSettings для обновления отображения
            toggleLotwSettings();
            updateLoTWValidation();
        });
        
        // Валидация полей LoTW
        const lotwInputs = document.querySelectorAll('input[name="lotw_user"], input[name="lotw_password"]');
        lotwInputs.forEach(input => {
            input.addEventListener('input', updateLoTWValidation);
            input.addEventListener('blur', updateLoTWValidation);
        });
        
        // Инициализация состояния при загрузке
        toggleLotwSettings();
    }
}

// Проверяем есть ли сохраненные данные LoTW
function hasLoTWData() {
    const lotwUser = document.querySelector('input[name="lotw_user"]')?.value.trim();
    const lotwPassword = document.querySelector('input[name="lotw_password"]')?.value.trim();
    
    // Проверяем поля ввода
    const hasInputData = (lotwUser && lotwUser.length > 0) || (lotwPassword && lotwPassword.length > 0);
    
    // Проверяем статусные элементы
    const hasSuccessStatus = document.querySelector('.status-item.success');
    const hasWarningStatus = document.querySelector('.status-item.warning');
    const hasInfoStatus = document.querySelector('.status-item.info');
    
    // Есть данные если есть поля ввода или любой статус LoTW
    const hasStatusData = hasSuccessStatus || hasWarningStatus || hasInfoStatus;
    
    const result = hasInputData || hasStatusData;
    console.log('🔍 Проверка данных LoTW:', {
        lotwUser: !!lotwUser,
        lotwPassword: !!lotwPassword,
        hasInputData,
        hasStatusData,
        result
    });
    
    return result;
}
    
function toggleLotwSettings() {
    const checkbox = document.getElementById('use_lotw');
    const settings = document.getElementById('lotw_settings');
    const consentCheckbox = document.getElementById('lotw_consent');
    
    if (checkbox && settings) {
        const isChecked = checkbox.checked;
        
        // Определяем, нужно ли показывать настройки
        let shouldShow = false;
        
        // Показываем если:
        // 1. Чекбокс "Активировать" включен ИЛИ
        // 2. Согласие дано ИЛИ  
        // 3. Есть сохраненные данные LoTW (включая неверные)
        if (isChecked) {
            shouldShow = true;
        } else if (consentCheckbox && consentCheckbox.checked) {
            shouldShow = true;
        } else if (hasLoTWData()) {
            shouldShow = true;
        }
        
        // Синхронизируем чекбоксы, но только если пользователь явно не снял галочку
        if (consentCheckbox && shouldShow && !consentCheckbox.checked) {
            consentCheckbox.checked = true;
        }
        
        settings.style.display = shouldShow ? 'block' : 'none';
        
        // Анимация появления
        if (shouldShow) {
            settings.style.opacity = '0';
            settings.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                settings.style.transition = 'all 0.3s ease';
                settings.style.opacity = '1';
                settings.style.transform = 'translateY(0)';
            }, 10);
        }
        
        console.log('🌐 LoTW настройки:', shouldShow ? 'показаны' : 'скрыты', 
                   '| checked:', isChecked, '| consent:', consentCheckbox?.checked, '| hasData:', hasLoTWData());
    }
}

function updateLoTWValidation() {
    const useLotwCheckbox = document.getElementById('use_lotw');
    const consentCheckbox = document.getElementById('lotw_consent');
    const lotwUserInput = document.querySelector('input[name="lotw_user"]');
    const lotwPasswordInput = document.querySelector('input[name="lotw_password"]');
    
    if (!useLotwCheckbox || !consentCheckbox) return;
    
    const isEnabled = useLotwCheckbox.checked;
    
    if (isEnabled) {
        // Включаем валидацию полей LoTW
        if (lotwUserInput) {
            lotwUserInput.required = true;
            lotwUserInput.addEventListener('input', validateLoTWUser);
        }
        if (lotwPasswordInput) {
            lotwPasswordInput.required = true;
        }
    } else {
        // Отключаем валидацию
        if (lotwUserInput) {
            lotwUserInput.required = false;
            lotwUserInput.removeEventListener('input', validateLoTWUser);
            clearValidationMessage(lotwUserInput);
        }
        if (lotwPasswordInput) {
            lotwPasswordInput.required = false;
            clearValidationMessage(lotwPasswordInput);
        }
    }
}

function validateLoTWUser() {
    const input = document.querySelector('input[name="lotw_user"]');
    if (!input) return;
    
    const callsign = input.value.trim().toUpperCase();
    
    // Простая проверка - только не пустой и содержит только разрешенные символы
    if (!callsign) {
        showValidationMessage(input, 'Логин LoTW не может быть пустым');
        return false;
    }
    
    // Проверяем только разрешенные символы
    const allowedPattern = /^[A-Z0-9\/]*$/;
    if (!allowedPattern.test(callsign)) {
        showValidationMessage(input, 'Используйте только латинские буквы, цифры и символ /');
        return false;
    }
    
    clearValidationMessage(input);
    return true;
}

window.verifyLotwCredentials = function() {
    console.log('🔍 Проверяем учетные данные LoTW...');
    
    const lotwUser = document.querySelector('input[name="lotw_user"]')?.value.trim();
    const lotwPassword = document.querySelector('input[name="lotw_password"]')?.value.trim();
    
    if (!lotwUser || !lotwPassword) {
        showNotification('⚠️ Пожалуйста, введите логин и пароль LoTW', 'warning');
        return;
    }

    // Убираем строгую валидацию - разрешаем любые символы кроме запрещенных
    const allowedPattern = /^[A-Z0-9\/]*$/;
    if (!allowedPattern.test(lotwUser.toUpperCase())) {
        showNotification('❌ Используйте только латинские буквы, цифры и символ /', 'error');
        return;
    }
    
    // Показываем индикатор загрузки
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<span>⏳</span> Проверяем...';
    button.disabled = true;

    // Создаем форму для отправки данных проверки
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

window.deleteLotwCredentials = function() {
    if (confirm('🗑️ Вы уверены, что хотите удалить сохраненные логин и пароль LoTW?')) {
        console.log('🗑️ Удаляем учетные данные LoTW');
        
        const form = createCSRFProtectedForm('/profile/delete-lotw/');
        document.body.appendChild(form);
        form.submit();
    }
};

// ========== УПРАВЛЕНИЕ ПАРОЛЕМ ==========

function initializePasswordChange() {
    const profileForm = document.getElementById('profile-edit-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(event) {
            console.log('📝 Отправка формы профиля');
            updateCallsignsData();
            updateFormValidation();
        });
    }
    
    // Валидация полей пароля в реальном времени
    const passwordFields = ['old_password', 'new_password', 'confirm_password'];
    passwordFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', validatePasswordFields);
            field.addEventListener('blur', validatePasswordFields);
        }
    });
}

function validatePasswordFields() {
    const oldPassword = document.getElementById('old_password');
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    
    // Очищаем все ошибки
    [oldPassword, newPassword, confirmPassword].forEach(field => {
        if (field) clearValidationMessage(field);
    });
    
    let isValid = true;
    
    // Проверяем, хочет ли пользователь менять пароль
    const wantsToChangePassword = newPassword && newPassword.value.trim().length > 0;
    
    if (wantsToChangePassword) {
        // Если пользователь хочет менять пароль, проверяем все поля
        
        // Проверяем длину нового пароля
        if (newPassword.value.length < 8) {
            showValidationMessage(newPassword, 'Пароль должен содержать минимум 8 символов');
            isValid = false;
        }
        
        // Проверяем совпадение паролей
        if (confirmPassword && newPassword.value !== confirmPassword.value) {
            showValidationMessage(confirmPassword, 'Пароли не совпадают');
            isValid = false;
        }
        
        // Проверяем, что введен текущий пароль
        if (oldPassword && !oldPassword.value.trim()) {
            showValidationMessage(oldPassword, 'Введите текущий пароль');
            isValid = false;
        }
    }
    
    return isValid;
}

window.changePassword = function() {
    console.log('🔑 Смена пароля');
    
    const oldPassword = document.getElementById('old_password')?.value.trim();
    const newPassword = document.getElementById('new_password')?.value.trim();
    const confirmPassword = document.getElementById('confirm_password')?.value.trim();

    // Проверяем, хочет ли пользователь менять пароль
    const wantsToChangePassword = newPassword && newPassword.length > 0;
    
    if (!wantsToChangePassword) {
        showNotification('ℹ️ Поля пароля не заполнены. Пароль не изменен.', 'info');
        return;
    }

    if (!validatePasswordFields()) {
        showNotification('❌ Исправьте ошибки в полях пароля', 'error');
        return;
    }
    
    if (!oldPassword) {
        showNotification('⚠️ Введите текущий пароль', 'warning');
        return;
    }

    // Показываем индикатор загрузки
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<span>⏳</span> Сохраняем...';
    button.disabled = true;

    const form = createCSRFProtectedForm('/profile/change-password/');
    
    const oldPasswordInput = document.createElement('input');
    oldPasswordInput.type = 'hidden';
    oldPasswordInput.name = 'old_password';
    oldPasswordInput.value = oldPassword;
    form.appendChild(oldPasswordInput);

    const newPasswordInput = document.createElement('input');
    newPasswordInput.type = 'hidden';
    newPasswordInput.name = 'new_password';
    newPasswordInput.value = newPassword;
    form.appendChild(newPasswordInput);

    const confirmPasswordInput = document.createElement('input');
    confirmPasswordInput.type = 'hidden';
    confirmPasswordInput.name = 'confirm_password';
    confirmPasswordInput.value = confirmPassword;
    form.appendChild(confirmPasswordInput);

    document.body.appendChild(form);
    form.submit();
    
    // Восстанавливаем кнопку через 10 секунд
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 10000);
};

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

function createCSRFProtectedForm(action) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = action;
    form.style.display = 'none';

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    if (!csrfToken) {
        showNotification('❌ Ошибка: CSRF токен не найден', 'error');
        throw new Error('CSRF токен не найден');
    }

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    return form;
}

function showNotification(message, type = 'info') {
    // Создаем уведомление
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️';
    alertDiv.innerHTML = `
        ${icon} ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function updateFormValidation() {
    // Обновляем валидацию всей формы
    updateCallsignsData();
    updateLoTWValidation();
    validatePasswordFields();
}

// ========== ГЛОБАЛЬНЫЕ ФУНКЦИИ ==========

// Делаем функции глобально доступными для onclick атрибутов
window.addCallsign = addCallsign;
window.removeCallsign = removeCallsign;
window.toggleLotwSettings = toggleLotwSettings;
window.verifyLotwCredentials = verifyLotwCredentials;
window.deleteLotwCredentials = deleteLotwCredentials;
window.changePassword = changePassword;

// Экспорт для отладки
window.ProfileEditor = {
    callsignsData,
    addCallsign,
    removeCallsign,
    updateCallsignsData,
    validateCallsign,
    showNotification
};

console.log('🚀 Улучшенный скрипт страницы профиля загружен');