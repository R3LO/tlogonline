// Login page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const messageDiv = document.getElementById('message');

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

    if (savedUsername && savedPassword && loginForm) {
        document.getElementById('username').value = savedUsername;
        document.getElementById('password').value = savedPassword;
        document.getElementById('rememberMe').checked = true;
    }

    // Show Django messages
    {% if messages %}
        if (messageDiv) {
            {% for message in messages %}
                messageDiv.className = 'alert alert-{{ message.tags|default:"info" }}';
                messageDiv.textContent = '{{ message|escapejs }}';
                messageDiv.classList.remove('d-none');
            {% endfor %}
        }
    {% endif %}

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