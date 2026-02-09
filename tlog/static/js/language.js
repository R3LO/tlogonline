// Language handling JavaScript
document.addEventListener('DOMContentLoaded', function() {
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

    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }

    // Intercept language change form submissions to ensure proper redirect
    const languageForms = document.querySelectorAll('form[action*="set_language"]');
    languageForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const languageInput = form.querySelector('input[name="language"]');
            if (languageInput) {
                // Save language to cookie for persistence
                setCookie('django_language', languageInput.value, 365);
                
                // Set next parameter to current page URL
                const nextInput = form.querySelector('input[name="next"]');
                if (nextInput) {
                    nextInput.value = window.location.pathname;
                } else {
                    // Create next input if it doesn't exist
                    const nextInputEl = document.createElement('input');
                    nextInputEl.type = 'hidden';
                    nextInputEl.name = 'next';
                    nextInputEl.value = window.location.pathname;
                    form.appendChild(nextInputEl);
                }
            }
            // Allow form to submit normally
        });
    });

    // Add click handlers to language dropdown items for better UX
    const languageButtons = document.querySelectorAll('form[action*="set_language"] button');
    languageButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            const languageInput = form.querySelector('input[name="language"]');
            if (languageInput) {
                // Set next parameter to current page URL
                const nextInput = form.querySelector('input[name="next"]');
                if (nextInput) {
                    nextInput.value = window.location.pathname;
                } else {
                    // Create next input if it doesn't exist
                    const nextInputEl = document.createElement('input');
                    nextInputEl.type = 'hidden';
                    nextInputEl.name = 'next';
                    nextInputEl.value = window.location.pathname;
                    form.appendChild(nextInputEl);
                }
            }
        });
    });

    // Detect language from browser only if no language is set
    const savedLanguage = getCookie('django_language');

    // Django's LocaleMiddleware handles language setting automatically
    // This script is kept for future language-related enhancements
});