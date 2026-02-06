document.addEventListener('DOMContentLoaded', function() {
    console.log('Profile edit JS initialized');
    
    // Инициализация
    initCallsignInputs();
    initProfileForm();
    initLotwSync();

    function initProfileForm() {
        const profileForm = document.getElementById('profile-edit-form');
        if (profileForm) {
            profileForm.addEventListener('submit', function(event) {
                console.log('Form submit triggered');
                updateCallsignsData();
                // Форма отправится естественным образом
            });
        }
    }

    function initLotwSync() {
        const useLotwCheckbox = document.getElementById('use_lotw');
        const consentCheckbox = document.getElementById('lotw_consent');
        
        if (useLotwCheckbox && consentCheckbox) {
            // Синхронизация чекбоксов
            useLotwCheckbox.addEventListener('change', function() {
                consentCheckbox.checked = this.checked;
                toggleLotwSettings();
            });
            
            consentCheckbox.addEventListener('change', function() {
                useLotwCheckbox.checked = this.checked;
                toggleLotwSettings();
            });
        }
    }

    // ========== Callsign Management ==========
    function initCallsignInputs() {
        console.log('Initializing callsign inputs');
        
        // Загрузка данных при загрузке страницы
        loadProfileData();
        
        // Инициализация обработчиков для существующих полей
        document.querySelectorAll('.callsign-input').forEach(input => {
            input.addEventListener('input', function() {
                // Автоматическое преобразование в верхний регистр и валидация
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
            });
            
            input.addEventListener('blur', function() {
                // Финальная валидация при потере фокуса
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
                updateCallsignsData();
            });
        });
    }
    
    function loadProfileData() {
        console.log('Loading profile data');
        
        let rawData = '';
        const scriptElement = document.getElementById('callsigns-data');
        if (scriptElement && scriptElement.textContent.trim()) {
            rawData = scriptElement.textContent.trim();
        } else {
            const jsonField = document.getElementById('my_callsigns_json');
            if (!jsonField) return;
            rawData = jsonField.value.trim();
        }

        console.log('Raw callsigns data:', rawData);

        if (!rawData || rawData === '[]') {
            console.log('No callsigns data found, adding empty input');
            addCallsign('');
            return;
        }

        try {
            let callsigns;
            try {
                callsigns = JSON.parse(rawData);
            } catch (parseError) {
                console.log('JSON parse error:', parseError);
                if (rawData.startsWith('[') && rawData.endsWith(']')) {
                    callsigns = [];
                } else {
                    callsigns = rawData.split(',').map(s => s.trim().replace(/[\'"]/g, '')).filter(s => s);
                }
            }

            console.log('Parsed callsigns:', callsigns);

            const container = document.getElementById('callsigns-container');
            container.innerHTML = '';

            if (Array.isArray(callsigns) && callsigns.length > 0) {
                callsigns.forEach(function(callsign) {
                    let callsignValue = '';
                    if (typeof callsign === 'string') {
                        callsignValue = callsign;
                    } else if (callsign && callsign.name) {
                        callsignValue = callsign.name;
                    }
                    addCallsign(callsignValue);
                });
                updateCallsignsData();
            } else {
                console.log('Empty callsigns array, adding empty input');
                addCallsign('');
            }
        } catch (error) {
            console.error('Error loading profile data:', error);
            addCallsign('');
        }
    }

    // Add new callsign input
    window.addCallsign = function(value = '') {
        console.log('Adding callsign:', value);
        
        const container = document.getElementById('callsigns-container');
        const item = document.createElement('div');
        item.className = 'callsign-item mb-2';
        item.innerHTML = `
            <input type="text" class="form-control callsign-input"
                   name="my_callsigns_names[]"
                   value="${value}"
                   placeholder="Позывной"
                   autocomplete="off"
                   maxlength="20">
            <button type="button" class="btn btn-outline-danger btn-sm remove-callsign-btn"
                    onclick="removeCallsign(this)">
                <span>✖</span>
            </button>
        `;
        container.appendChild(item);
        
        // Инициализируем обработчики для нового поля
        const newInput = item.querySelector('.callsign-input');
        if (newInput) {
            newInput.addEventListener('input', function() {
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
            });
            
            newInput.addEventListener('blur', function() {
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
                updateCallsignsData();
            });
        }

        updateCallsignsData();
        console.log('Callsign added successfully');
    };

    // Remove callsign input
    window.removeCallsign = function(button) {
        console.log('Removing callsign');
        const item = button.closest('.callsign-item');
        if (item) {
            item.remove();
            updateCallsignsData();
            console.log('Callsign removed successfully');
        }
    };

    // Функция для обновления данных позывных в скрытом поле
    window.updateCallsignsData = function() {
        console.log('Updating callsigns data');
        
        const callsigns = [];
        const container = document.getElementById('callsigns-container');
        const items = container.querySelectorAll('.callsign-item');

        items.forEach(function(item) {
            const input = item.querySelector('input[name="my_callsigns_names[]"]');
            if (input) {
                const name = input.value.trim().toUpperCase();
                if (name && name.match(/^[A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3}[A-Z]$/)) {
                    callsigns.push(name);
                } else if (name) {
                    // Валидация позывного
                    console.warn('Invalid callsign format:', name);
                }
            }
        });

        const jsonField = document.getElementById('my_callsigns_json');
        if (jsonField) {
            jsonField.value = JSON.stringify(callsigns);
            console.log('Updated callsigns JSON:', jsonField.value);
        }
        
        return callsigns;
    };

    // ========== LoTW Toggle ==========
    window.toggleLotwSettings = function() {
        console.log('Toggling LoTW settings');
        
        const checkbox = document.getElementById('use_lotw');
        const settings = document.getElementById('lotw_settings');
        if (checkbox && settings) {
            settings.style.display = checkbox.checked ? 'block' : 'none';
            console.log('LoTW settings display:', settings.style.display);
        }
    };

    // ========== LoTW Credentials Management ==========
    window.verifyLotwCredentials = function() {
        console.log('Verifying LoTW credentials');
        
        const lotwUser = document.querySelector('input[name="lotw_user"]')?.value.trim();
        const lotwPassword = document.querySelector('input[name="lotw_password"]')?.value.trim();
        
        if (!lotwUser || !lotwPassword) {
            alert('Пожалуйста, введите логин и пароль LoTW');
            return;
        }

        // Валидация позывного
        const callsignPattern = /^[A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3}[A-Z]$/;
        if (!callsignPattern.test(lotwUser.toUpperCase())) {
            alert('Неверный формат позывного. Используйте только буквы и цифры (например: UA1ABC)');
            return;
        }

        // Показываем индикатор загрузки
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<span>⏳</span> Проверяем...';
        button.disabled = true;

        // Создаем форму для отправки данных проверки
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/profile/verify-lotw/';
        form.style.display = 'none';

        // Добавляем CSRF токен
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
        if (!csrfToken) {
            alert('Ошибка: CSRF токен не найден');
            button.innerHTML = originalText;
            button.disabled = false;
            return;
        }

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);

        // Добавляем поля логина и пароля
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
    };

    window.deleteLotwCredentials = function() {
        if (confirm('Вы уверены, что хотите удалить сохраненные логин и пароль LoTW?')) {
            console.log('Deleting LoTW credentials');
            
            // Создаем форму для отправки данных удаления
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/profile/delete-lotw/';
            form.style.display = 'none';

            // Добавляем CSRF токен
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
            if (!csrfToken) {
                alert('Ошибка: CSRF токен не найден');
                return;
            }

            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);

            document.body.appendChild(form);
            form.submit();
        }
    };

    // ========== Password Change ==========
    window.changePassword = function() {
        console.log('Changing password');
        
        const oldPassword = document.getElementById('old_password')?.value.trim();
        const newPassword = document.getElementById('new_password')?.value.trim();
        const confirmPassword = document.getElementById('confirm_password')?.value.trim();

        if (!oldPassword || !newPassword || !confirmPassword) {
            alert('Пожалуйста, заполните все поля для смены пароля');
            return;
        }

        if (newPassword !== confirmPassword) {
            alert('Новый пароль и подтверждение пароля не совпадают');
            return;
        }

        if (newPassword.length < 8) {
            alert('Пароль должен содержать минимум 8 символов');
            return;
        }

        // Показываем индикатор загрузки
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<span>⏳</span> Сохраняем...';
        button.disabled = true;

        // Создаем форму для отправки данных смены пароля
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/profile/change-password/';
        form.style.display = 'none';

        // Добавляем CSRF токен
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
        if (!csrfToken) {
            alert('Ошибка: CSRF токен не найден');
            button.innerHTML = originalText;
            button.disabled = false;
            return;
        }

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);

        // Добавляем поля паролей
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
    };

    // Initialize LoTW settings on page load
    const useLotwCheckbox = document.getElementById('use_lotw');
    const lotwSettings = document.getElementById('lotw_settings');
    
    if (useLotwCheckbox && lotwSettings) {
        // Check if user has LoTW credentials
        const lotwUser = document.querySelector('input[name="lotw_user"]')?.value.trim();
        const lotwPassword = document.querySelector('input[name="lotw_password"]')?.value.trim();
        
        if (lotwUser || lotwPassword) {
            lotwSettings.style.display = 'block';
            useLotwCheckbox.checked = true;
            const consentCheckbox = document.getElementById('lotw_consent');
            if (consentCheckbox) {
                consentCheckbox.checked = true;
            }
        } else {
            lotwSettings.style.display = 'none';
            useLotwCheckbox.checked = false;
            const consentCheckbox = document.getElementById('lotw_consent');
            if (consentCheckbox) {
                consentCheckbox.checked = false;
            }
        }
    }

    console.log('Profile edit JS initialization complete');
});
