// Profile Edit JavaScript - ПОЛНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ
// ========================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== Инициализация при загрузке страницы ==========
    
    function initProfileEdit() {
        
        // Загружаем данные из базы в форму
        loadProfileData();
        
        // Инициализируем обработчики событий
        initEventHandlers();
        
        // Инициализируем поля ввода позывных
        initCallsignInputs();
        
        // Инициализируем LoTW настройки
        initLotwSettings();
    }
    
    // Загрузка данных профиля при загрузке страницы
    function loadProfileData() {
        
        // Сначала пробуем получить данные из script тега
        let rawData = '';
        const scriptElement = document.getElementById('callsigns-data');
        if (scriptElement && scriptElement.textContent.trim()) {
            rawData = scriptElement.textContent.trim();
        } else {
            // Если script тега нет, используем input поле
            const jsonField = document.getElementById('my_callsigns_json');
            if (!jsonField) {
                console.error('Neither script tag nor input field found!');
                return;
            }
            rawData = jsonField.value.trim();
        }
        
        if (!rawData || rawData === '[]') {
            // Не добавляем поле автоматически - пользователь сам нажмет кнопку "Добавить позывной"
            return;
        }
        
        try {
            let callsigns;
            
            // Пытаемся распарсить как JSON
            try {
                callsigns = JSON.parse(rawData);
            } catch (parseError) {
                // console.log removed
                if (rawData.startsWith('[') && rawData.endsWith(']')) {
                    callsigns = [];
                } else {
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
                        // Простой список строк - просто добавляем как есть
                        addCallsign(callsign);
                    });
                    
                    // console.log removed
                    
                    // ВАЖНО: Обновляем скрытое поле после загрузки
                    updateCallsignsData();
                } else {
                    // console.log removed
                    // Не добавляем пустое поле автоматически
                }
            } else {
                console.error('Invalid callsigns data format:', callsigns);
                // Не добавляем пустое поле при ошибке
            }
            
        } catch (error) {
            console.error('Error loading profile data:', error);
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
        // console.log removed
        
        // ВАЖНО: Обновляем данные позывных после добавления
        updateCallsignsData();
    };
    
    // Remove callsign input
    window.removeCallsign = function(button) {
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
        
        // ВАЖНО: Обновляем скрытое поле сразу после удаления
        updateCallsignsData();
        
        // Если после удаления не осталось полей, ничего не добавляем автоматически
        // Пользователь сам может добавить поле кнопкой "Добавить позывной"
    };
    
    // Функция для обновления данных позывных в скрытом поле
    function updateCallsignsData() {
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
                    callsigns.push(name.toUpperCase());
                }
            }
        });

        const jsonField = document.getElementById('my_callsigns_json');
        if (jsonField) {
            const jsonValue = JSON.stringify(callsigns);
            jsonField.value = jsonValue;
            // console.log removed
        } else {
            console.error('my_callsigns_json field not found!');
        }
    }
    
    // ========== Event Handlers ==========
    
    function initEventHandlers() {
        const form = document.getElementById('profile-edit-form');
        if (!form) {
            console.error('Profile form not found!');
            return;
        }
        
        // Form submit handler
        form.addEventListener('submit', function(e) {
            // console.log removed
            // console.log removed
            
            // ВАЖНО: Обновляем данные перед отправкой
            updateCallsignsData();
            
            // Debug: проверим данные формы
            const formData = new FormData(this);
            console.log('Form data my_callsigns_json:', formData.get('my_callsigns_json'));
            
            // Показываем сообщение пользователю
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Сохранение...';
                submitBtn.disabled = true;
            }
                
            // Позволяем форме отправиться на сервер
            // return false; // УБРАНО - теперь форма отправляется на сервер
        });
        
        // ========== LoTW Toggle ==========
        window.toggleLotwSettings = function() {
            const checkbox = document.getElementById('use_lotw');
            const settings = document.getElementById('lotw_settings');
            settings.style.display = checkbox.checked ? 'block' : 'none';
            document.cookie = `use_lotw=${checkbox.checked}; path=/; max-age=${30 * 24 * 60 * 60}`;
        };

        // Add event listener for LoTW checkbox
        const useLotwCheckbox = document.getElementById('use_lotw');
        if (useLotwCheckbox) {
            useLotwCheckbox.addEventListener('change', function() {
                toggleLotwSettings();
            });
        }

        // ========== Verify LoTW ==========
        const verifyBtn = document.getElementById('verify_lotw');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', function() {
                const lotwBlock = document.getElementById('lotw_settings');
                const login = lotwBlock.querySelector('input[name="lotw_user"]').value.trim();
                const password = lotwBlock.querySelector('input[name="lotw_password"]').value;
                const button = this;
                const statusDiv = document.getElementById('lotw_status');

                if (!login || !password) {
                    alert('Введите логин и пароль от LoTW');
                    return;
                }

                button.disabled = true;
                button.innerHTML = '<span>⏳</span> Проверка...';

                fetch('/dashboard/profile/verify-lotw/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                    },
                    body: JSON.stringify({ login: login, password: password })
                })
                .then(response => response.json())
                .then(data => {
                    button.disabled = false;
                    button.innerHTML = '<span>🔍</span> Проверить логин и пароль';

                    if (data.success && data.is_valid) {
                        statusDiv.innerHTML = '<span class="badge bg-success">✓ Логин и пароль верны и сохранены</span>';
                        document.getElementById('use_lotw').checked = true;
                        document.cookie = `use_lotw=true; path=/; max-age=${30 * 24 * 60 * 60}`;
                        
                        // ВАЖНО: Автоматически сохраняем данные в базу данных через основную форму
                        saveLotwToDatabase(login, password);
                        
                    } else {
                        statusDiv.innerHTML = '<span class="badge bg-danger">✗ Логин или пароль неверны</span>';
                    }
                })
                .catch(error => {
                    button.disabled = false;
                    button.innerHTML = '<span>🔍</span> Проверить логин и пароль';
                    alert('Ошибка при проверке: ' + error.message);
                });
            });
        }

        // ========== Delete LoTW ==========
        const deleteBtn = document.getElementById('delete_lotw');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                const lotwBlock = document.getElementById('lotw_settings');
                lotwBlock.querySelector('input[name="lotw_user"]').value = '';
                lotwBlock.querySelector('input[name="lotw_password"]').value = '';
                document.getElementById('lotw_status').innerHTML = '';
                document.getElementById('use_lotw').checked = false;
                lotwBlock.style.display = 'none';
                document.cookie = `use_lotw=false; path=/; max-age=${30 * 24 * 60 * 60}`;

                fetch('/dashboard/profile/delete-lotw/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                    }
                });
            });
        }
        
        // ========== Password Change ==========
        const changePasswordBtn = document.getElementById('change_password_btn');
        if (changePasswordBtn) {
            changePasswordBtn.addEventListener('click', function() {
                document.getElementById('password_change_section').style.display = 'block';
            });
        }

        const cancelPasswordBtn = document.getElementById('cancel_password_btn');
        if (cancelPasswordBtn) {
            cancelPasswordBtn.addEventListener('click', function() {
                document.getElementById('password_change_section').style.display = 'none';
                document.getElementById('new_password1').value = '';
                document.getElementById('new_password2').value = '';
                document.getElementById('new_password1').classList.remove('is-invalid');
                document.getElementById('new_password2').classList.remove('is-invalid');
            });
        }

        const savePasswordBtn = document.getElementById('save_password_btn');
        if (savePasswordBtn) {
            savePasswordBtn.addEventListener('click', function() {
                const password1 = document.getElementById('new_password1').value;
                const password2 = document.getElementById('new_password2').value;
                const btn = this;

                document.getElementById('new_password1').classList.remove('is-invalid');
                document.getElementById('new_password2').classList.remove('is-invalid');

                if (!password1) {
                    document.getElementById('new_password1').classList.add('is-invalid');
                    return;
                }

                if (password1.length < 8) {
                    document.getElementById('new_password1').classList.add('is-invalid');
                    return;
                }

                if (password1 !== password2) {
                    document.getElementById('new_password2').classList.add('is-invalid');
                    return;
                }

                btn.disabled = true;
                btn.innerHTML = '<span>⏳</span> Сохранение...';

                fetch('/dashboard/profile/change-password/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
                    },
                    body: JSON.stringify({ password: password1 })
                })
                .then(response => response.json())
                .then(data => {
                    btn.disabled = false;
                    btn.innerHTML = '<span>💾</span> Сохранить пароль';

                    if (data.success) {
                        alert('Пароль успешно изменён!');
                        document.getElementById('password_change_section').style.display = 'none';
                        document.getElementById('new_password1').value = '';
                        document.getElementById('new_password2').value = '';
                    } else {
                        alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
                    }
                })
                .catch(error => {
                    btn.disabled = false;
                    btn.innerHTML = '<span>💾</span> Сохранить пароль';
                    alert('Ошибка при изменении пароля: ' + error.message);
                });
            });
        }

        // ========== Email Validation ==========
        const emailInput = document.querySelector('input[name="email"]');
        if (emailInput) {
            emailInput.addEventListener('change', function() {
                const email = this.value.trim();
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

                if (email && !emailRegex.test(email)) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                }
            });
        }
        
        // console.log removed
    }
    
    // ========== LoTW Settings ==========
    
    function initLotwSettings() {
        const lotwUser = document.querySelector('input[name="lotw_user"]').value.trim();
        const lotwPassword = document.querySelector('input[name="lotw_password"]').value.trim();
        const settings = document.getElementById('lotw_settings');
        const checkbox = document.getElementById('use_lotw');

        // If user has LoTW credentials, show settings by default
        if (lotwUser || lotwPassword) {
            settings.style.display = 'block';
            if (checkbox) checkbox.checked = true;
            document.cookie = `use_lotw=true; path=/; max-age=${30 * 24 * 60 * 60}`;
        } else {
            // Check cookie for saved preference
            const cookies = document.cookie.split(';').reduce((acc, cookie) => {
                const [key, value] = cookie.trim().split('=');
                acc[key] = value;
                return acc;
            }, {});

            if (cookies['use_lotw'] === 'true') {
                settings.style.display = 'block';
                if (checkbox) checkbox.checked = true;
            } else {
                settings.style.display = 'none';
                if (checkbox) checkbox.checked = false;
            }
        }
    }
    
    // ========== Success Message Handling ==========
    // Если есть сообщение об успехе, перезагружаем страницу через некоторое время
    const alerts = document.querySelectorAll('.alert-success');
    if (alerts.length > 0) {
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }
    
    // ========== LoTW Auto-Save Function ==========
    function saveLotwToDatabase(login, password) {
        // console.log removed
        
        // Проверяем, не находимся ли мы уже в процессе автосохранения
        if (window.lotwAutoSaving) {
            // console.log removed
            return;
        }
        
        window.lotwAutoSaving = true; // Устанавливаем флаг
        
        const form = document.getElementById('profile-edit-form');
        if (!form) {
            console.error('Profile form not found!');
            window.lotwAutoSaving = false;
            return;
        }
        
        // Создаем FormData из формы
        const formData = new FormData(form);
        
        // Обновляем данные LoTW в FormData
        formData.set('lotw_user', login);
        formData.set('lotw_password', password);
        formData.set('use_lotw', 'on'); // Устанавливаем чекбокс
        
        // Обновляем скрытое поле с позывными
        updateCallsignsData();
        formData.set('my_callsigns_json', document.getElementById('my_callsigns_json').value);
        
        // Отправляем данные на сервер
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
            }
        })
        .then(response => {
            window.lotwAutoSaving = false; // Сбрасываем флаг
            
            if (response.ok) {
                // console.log removed
                // Перезагружаем страницу для обновления данных
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                console.error('❌ Failed to auto-save LoTW data');
            }
        })
        .catch(error => {
            window.lotwAutoSaving = false; // Сбрасываем флаг даже при ошибке
            console.error('Error auto-saving LoTW data:', error);
        });
    }
    
    // ========== Initialize ==========
    
    initProfileEdit();
});
