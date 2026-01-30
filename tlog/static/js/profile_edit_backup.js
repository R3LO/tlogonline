// Profile Edit JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // console.log removed // Debug log
    
    // ========== Callsign Management Functions ==========
    
    // Initialize handlers for existing callsign inputs
    function initCallsignInputs() {
        document.querySelectorAll('.callsign-input').forEach(input => {
            // Убираем существующие обработчики, чтобы избежать дублирования
            const newInput = input.cloneNode(true);
            input.parentNode.replaceChild(newInput, input);
            
            // Добавляем новый обработчик
            newInput.addEventListener('input', function() {
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
            });
        });
        
        console.log('Initialized callsign inputs:', document.querySelectorAll('.callsign-input').length); // Debug log
    }

    // Add new callsign input
    window.addCallsign = function() {
        const container = document.getElementById('callsigns-container');
        const item = document.createElement('div');
        item.className = 'my-callsign-item';
        item.innerHTML = `
            <input type="text" class="form-control name-input callsign-input"
                   name="my_callsigns_names[]"
                   value=""
                   placeholder="Позывной"
                   autocomplete="off">
            <button type="button" class="btn btn-outline-danger btn-sm"
                    onclick="removeCallsign(this)">
                ✕
            </button>
        `;
        container.appendChild(item);
        
        // Инициализируем обработчики для нового поля
        initCallsignInputs();
        
        // console.log removed // Debug log
    };

    // Remove callsign input
    window.removeCallsign = function(button) {
        const container = document.getElementById('callsigns-container');
        const items = container.querySelectorAll('.my-callsign-item');
        
        if (items.length > 1) {
            // Удаляем элемент
            const item = button.closest('.my-callsign-item');
            item.remove();
            // console.log removed // Debug log
        } else {
            // Если это последний элемент, просто очищаем его
            const item = button.closest('.my-callsign-item');
            const input = item.querySelector('input');
            input.value = '';
            // console.log removed // Debug log
        }
    };
    
    // ========== Form Submit Handler ==========
    const profileForm = document.querySelector('form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            // console.log removed // Debug log
            // console.log removed // Debug log
            
            const callsigns = [];
            const container = document.getElementById('callsigns-container');
            const items = container.querySelectorAll('.my-callsign-item');

            // console.log removed // Debug log
            
            items.forEach(function(item, index) {
                const input = item.querySelector('input[name="my_callsigns_names[]"]');
                if (input) {
                    const name = input.value.trim();
                    // console.log removed // Debug log
                    if (name) {
                        callsigns.push({
                            name: name.toUpperCase()
                        });
                    }
                }
            });

            // console.log removed // Debug log
            
            const jsonField = document.getElementById('my_callsigns_json');
            if (jsonField) {
                const jsonValue = JSON.stringify(callsigns);
                jsonField.value = jsonValue;
                // console.log removed // Debug log
                
                // Дополнительная проверка
                // console.log removed // Debug log
            } else {
                console.error('my_callsigns_json field not found!'); // Debug log
            }
            
            // Проверяем, что данные попали в форму
            const formData = new FormData(this);
            console.log('Form data my_callsigns_json:', formData.get('my_callsigns_json')); // Debug log
        });
    } else {
        console.error('Profile form not found!'); // Debug log
    }

    // ========== Success Message Handling ==========
    // Если есть сообщение об успехе, перезагружаем страницу через некоторое время
    const alerts = document.querySelectorAll('.alert-success');
    if (alerts.length > 0) {
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }

    // ========== LoTW Toggle ==========
    window.toggleLotwSettings = function() {
        const checkbox = document.getElementById('use_lotw');
        const settings = document.getElementById('lotw_settings');
        settings.style.display = checkbox.checked ? 'block' : 'none';
        document.cookie = `use_lotw=${checkbox.checked}; path=/; max-age=${30 * 24 * 60 * 60}`;
    };

    // Initialize LoTW settings visibility based on profile data
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

    // Initialize LoTW settings on page load
    initLotwSettings();

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
    document.getElementById('change_password_btn').addEventListener('click', function() {
        document.getElementById('password_change_section').style.display = 'block';
    });

    document.getElementById('cancel_password_btn').addEventListener('click', function() {
        document.getElementById('password_change_section').style.display = 'none';
        document.getElementById('new_password1').value = '';
        document.getElementById('new_password2').value = '';
        document.getElementById('new_password1').classList.remove('is-invalid');
        document.getElementById('new_password2').classList.remove('is-invalid');
    });

    document.getElementById('save_password_btn').addEventListener('click', function() {
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

    // ========== Email Validation ==========
    document.querySelector('input[name="email"]').addEventListener('change', function() {
        const email = this.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (email && !emailRegex.test(email)) {
            this.classList.add('is-invalid');
        } else {
            this.classList.remove('is-invalid');
        }
    });
    
    // ========== Debug Info ==========
    // console.log removed // Debug log
});