// Form validation and input handling for registration page
document.addEventListener('DOMContentLoaded', function() {
    const callsignInput = document.getElementById('callsign');
    const qthLocatorInput = document.getElementById('qth_locator');
    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('password');
    const passwordConfirmInput = document.getElementById('password_confirm');

    // Convert callsign to uppercase
    if (callsignInput) {
        callsignInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    }

    // Convert QTH locator to uppercase
    if (qthLocatorInput) {
        qthLocatorInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });

        // Validate QTH locator format
        qthLocatorInput.addEventListener('blur', function(e) {
            const qth = e.target.value.toUpperCase();
            if (qth && !/^[A-Z]{2}\d{2}[A-Z]{0,2}$/.test(qth)) {
                e.target.setCustomValidity('Неверный формат QTH локатора (например: KO85UU)');
            } else {
                e.target.setCustomValidity('');
            }
        });
    }

    // Form validation on submit
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = passwordInput.value;
            const passwordConfirm = passwordConfirmInput.value;

            if (password !== passwordConfirm) {
                e.preventDefault();
                alert('Пароли не совпадают!');
                return false;
            }

            if (password.length < 8) {
                e.preventDefault();
                alert('Пароль должен содержать минимум 8 символов!');
                return false;
            }

            // Convert callsign to uppercase before submit
            callsignInput.value = callsignInput.value.toUpperCase();
            return true;
        });
    }
});