document.addEventListener('DOMContentLoaded', function() {
    // Инициализация управления позывными
    initCallsignInputs();
    initProfileForm();

    function initProfileForm() {
        const profileForm = document.getElementById('profile-edit-form');
        if (profileForm) {
            profileForm.addEventListener('submit', function(event) {
                // Обновляем данные позывных перед отправкой
                updateCallsignsData();
                // Форма отправится естественным образом
            });
        }
    }

    // ========== Callsign Management ==========
    function initCallsignInputs() {
        const jsonField = document.getElementById('my_callsigns_json');
        if (!jsonField) {
            return;
        }
        
        // Загрузка данных при загрузке страницы
        loadProfileData();
        
        // Инициализация обработчиков для существующих полей
        document.querySelectorAll('.callsign-input').forEach(input => {
            input.addEventListener('input', function() {
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
            });
        });
    }

    function loadProfileData() {
        let rawData = '';
        const scriptElement = document.getElementById('callsigns-data');
        if (scriptElement && scriptElement.textContent.trim()) {
            rawData = scriptElement.textContent.trim();
        } else {
            const jsonField = document.getElementById('my_callsigns_json');
            if (!jsonField) return;
            rawData = jsonField.value.trim();
        }

        if (!rawData || rawData === '[]') return;

        try {
            let callsigns;
            try {
                callsigns = JSON.parse(rawData);
            } catch (parseError) {
                if (rawData.startsWith('[') && rawData.endsWith(']')) {
                    callsigns = [];
                } else {
                    callsigns = rawData.split(',').map(s => s.trim()).filter(s => s);
                }
            }

            const container = document.getElementById('callsigns-container');
            container.innerHTML = '';

            if (Array.isArray(callsigns) && callsigns.length > 0) {
                callsigns.forEach(function(callsign) {
                    addCallsign(callsign);
                });
                updateCallsignsData();
            }
        } catch (error) {
            // Игнорируем ошибки
        }
    }
    
    // Add new callsign input
    window.addCallsign = function(value = '') {
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
        
        initCallsignInputs();
        updateCallsignsData();
    };

    // Remove callsign input
    window.removeCallsign = function(button) {
        const item = button.closest('.my-callsign-item');
        item.remove();
        updateCallsignsData();
    };

    // Функция для обновления данных позывных в скрытом поле
    window.updateCallsignsData = function() {
        const callsigns = [];
        const container = document.getElementById('callsigns-container');
        const items = container.querySelectorAll('.my-callsign-item');

        items.forEach(function(item) {
            const input = item.querySelector('input[name="my_callsigns_names[]"]');
            if (input) {
                const name = input.value.trim();
                if (name) {
                    callsigns.push(name.toUpperCase());
                }
            }
        });

        const jsonField = document.getElementById('my_callsigns_json');
        if (jsonField) {
            jsonField.value = JSON.stringify(callsigns);
        }
    };

    // ========== LoTW Toggle ==========
    window.toggleLotwSettings = function() {
        const checkbox = document.getElementById('use_lotw');
        const settings = document.getElementById('lotw_settings');
        if (checkbox && settings) {
            settings.style.display = checkbox.checked ? 'block' : 'none';
        }
    };

    // ========== LoTW Credentials Management ==========
    window.verifyLotwCredentials = function() {
        const lotwUser = document.querySelector('input[name="lotw_user"]')?.value.trim();
        const lotwPassword = document.querySelector('input[name="lotw_password"]')?.value.trim();
        
        if (!lotwUser || !lotwPassword) {
            alert('Пожалуйста, введите логин и пароль LoTW');
            return;
        }

        // Создаем форму для отправки данных проверки
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/profile/verify-lotw/';
        form.style.display = 'none';

        // Добавляем CSRF токен
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
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
            // Создаем форму для отправки данных удаления
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/profile/delete-lotw/';
            form.style.display = 'none';

            // Добавляем CSRF токен
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);

            document.body.appendChild(form);
            form.submit();
        }
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
        } else {
            lotwSettings.style.display = 'none';
            useLotwCheckbox.checked = false;
        }

        useLotwCheckbox.addEventListener('change', function() {
            toggleLotwSettings();
        });
    }
});
