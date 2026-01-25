// Profile Edit JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // ========== Callsign Inputs ==========
    // Initialize callsign inputs
    initCallsignInputs();

    // Add new callsign
    window.addCallsign = function() {
        const container = document.getElementById('callsigns-container');
        const item = document.createElement('div');
        item.className = 'my-callsign-item';
        item.innerHTML = `
            <input type="text" class="form-control name-input callsign-input"
                   name="my_callsigns_names[]"
                   placeholder="Позывной"
                   autocomplete="off">
            <button type="button" class="btn btn-outline-danger btn-sm"
                    onclick="removeCallsign(this)">
                ✕
            </button>
        `;
        container.appendChild(item);
        initCallsignInputs();
    };

    // Remove callsign
    window.removeCallsign = function(button) {
        const container = document.getElementById('callsigns-container');
        const items = container.querySelectorAll('.my-callsign-item');
        if (items.length > 1) {
            button.closest('.my-callsign-item').remove();
        } else {
            const item = button.closest('.my-callsign-item');
            item.querySelectorAll('input').forEach(input => input.value = '');
        }
    };

    function initCallsignInputs() {
        document.querySelectorAll('.callsign-input').forEach(input => {
            input.addEventListener('input', function() {
                this.value = this.value.toUpperCase();
            });
        });
    }

    // ========== Form Submit ==========
    document.querySelector('form').addEventListener('submit', function(e) {
        const callsigns = [];
        const container = document.getElementById('callsigns-container');
        const items = container.querySelectorAll('.my-callsign-item');

        items.forEach(item => {
            const name = item.querySelector('input[name="my_callsigns_names[]"]').value.trim();
            if (name) {
                callsigns.push({
                    name: name.toUpperCase()
                });
            }
        });

        document.getElementById('my_callsigns_json').value = JSON.stringify(callsigns);
    });

    // ========== Reload on Success ==========
    const alerts = document.querySelectorAll('.alert-success');
    if (alerts.length > 0) {
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }

    // ========== QTH Locator Uppercase ==========
    document.querySelector('input[name="my_gridsquare"]').addEventListener('input', function() {
        this.value = this.value.toUpperCase();
    });

    // ========== LoTW Toggle ==========
    window.toggleLotwSettings = function() {
        const checkbox = document.getElementById('use_lotw');
        const settings = document.getElementById('lotw_settings');
        settings.style.display = checkbox.checked ? 'block' : 'none';
        document.cookie = `use_lotw=${checkbox.checked}; path=/; max-age=${30 * 24 * 60 * 60}`;
    };

    // Load LoTW state from cookie
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
    }, {});

    if (cookies['use_lotw'] === 'true') {
        document.getElementById('use_lotw').checked = true;
        document.getElementById('lotw_settings').style.display = 'block';
    } else {
        document.getElementById('use_lotw').checked = false;
        document.getElementById('lotw_settings').style.display = 'none';
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
            document.getElementById('lotw_settings').style.display = 'none';
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
});