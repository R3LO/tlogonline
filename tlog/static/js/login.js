// Login page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');

    // Cookie helper functions
    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    // Load saved credentials on page load
    const savedUsername = getCookie('remembered_username');
    const savedPassword = getCookie('remembered_password');

    if (savedUsername && loginForm) {
        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');
        const rememberMeCheckbox = document.getElementById('rememberMe');

        if (usernameInput && savedUsername) {
            usernameInput.value = savedUsername;
        }
        if (passwordInput && savedPassword) {
            passwordInput.value = savedPassword;
        }
        if (rememberMeCheckbox) {
            rememberMeCheckbox.checked = true;
        }
    }

    // Convert callsign to uppercase on submit
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            const usernameInput = document.getElementById('username');
            if (usernameInput) {
                usernameInput.value = usernameInput.value.toUpperCase();
            }
        });
    }
});