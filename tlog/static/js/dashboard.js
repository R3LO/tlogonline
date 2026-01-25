// Dashboard JavaScript - QSO Form, Chat, and Utilities

// Cookie helper functions
function getCookieValue(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    return '';
}

function setCookieValue(name, value, days = 365) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = name + '=' + encodeURIComponent(value) + ';expires=' + expires.toUTCString() + ';path=/';
}

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

// ========== QSO Form Logic ==========
document.addEventListener('DOMContentLoaded', function() {
    const qsoForm = document.getElementById('qsoForm');
    const qsoInputForm = document.getElementById('qsoInputForm');
    const toggleText = document.getElementById('qsoFormToggleText');

    // Toggle button text
    if (qsoForm && toggleText) {
        qsoForm.addEventListener('shown.bs.collapse', function() {
            toggleText.textContent = 'Свернуть';
        });
        qsoForm.addEventListener('hidden.bs.collapse', function() {
            toggleText.textContent = 'Развернуть';
        });
    }

    // Set current date and time
    const dateInput = document.querySelector('input[name="date"]');
    const timeInput = document.querySelector('input[name="time"]');

    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    if (timeInput && !timeInput.value) {
        const now = new Date();
        timeInput.value = now.getHours().toString().padStart(2, '0') + ':' +
                         now.getMinutes().toString().padStart(2, '0');
    }

    // Convert callsigns to uppercase
    const callsignInputs = document.querySelectorAll('input[name="my_callsign"], input[name="callsign"]');
    callsignInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
        });
    });

    // Convert QTH locators to uppercase
    const gridsquareInputs = document.querySelectorAll('input[name="his_gridsquare"], input[name="my_gridsquare"]');
    gridsquareInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        });
    });

    // All text fields to uppercase
    const qsoTextFields = document.querySelectorAll('#qsoInputForm input[type="text"]');
    qsoTextFields.forEach(field => {
        if (field.name && !['date', 'time', 'frequency', 'cqz', 'ituz'].includes(field.name)) {
            field.addEventListener('input', function() {
                this.value = this.value.toUpperCase();
            });
        }
    });

    // SAT QSO checkbox toggle
    const satQsoCheckbox = document.getElementById('sat_qso');
    const satFields = document.getElementById('sat_fields');
    if (satQsoCheckbox && satFields) {
        const savedSatQso = getCookieValue('qso_sat_qso');
        if (savedSatQso === 'true') {
            satQsoCheckbox.checked = true;
            satFields.style.display = 'flex';
        } else {
            satQsoCheckbox.checked = false;
            satFields.style.display = 'none';
        }

        satQsoCheckbox.addEventListener('change', function() {
            satFields.style.display = this.checked ? 'flex' : 'none';
            setCookieValue('qso_sat_qso', this.checked, 365);
            if (!this.checked) {
                satFields.querySelector('select[name="prop_mode"]').value = '';
                satFields.querySelector('input[name="sat_name"]').value = '';
            }
        });
    }

    // QSO form state
    const qsoFormCollapsed = getCookieValue('qso_form_collapsed');
    if (qsoFormCollapsed !== 'true' && qsoForm && !qsoForm.classList.contains('show')) {
        qsoForm.classList.add('show');
        const toggleBtn = document.querySelector('[data-bs-target="#qsoForm"]');
        if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'true');
    }

    if (qsoForm) {
        qsoForm.addEventListener('shown.bs.collapse', function() {
            setCookieValue('qso_form_collapsed', 'false', 365);
        });
        qsoForm.addEventListener('hidden.bs.collapse', function() {
            setCookieValue('qso_form_collapsed', 'true', 365);
        });
    }

    // Load cookie fields
    const cookieFields = document.querySelectorAll('.cookie-field');
    cookieFields.forEach(field => {
        const cookieName = field.dataset.cookie;
        const value = getCookieValue(cookieName);
        if (value) {
            field.value = decodeURIComponent(value);
        }
    });

    // Form submission
    if (qsoInputForm) {
        qsoInputForm.addEventListener('submit', function(e) {
            const textFields = qsoInputForm.querySelectorAll('input[type="text"], input[type="search"]');
            textFields.forEach(field => {
                field.value = field.value.toUpperCase();
            });

            const satQsoCheckbox = document.getElementById('sat_qso');
            if (satQsoCheckbox) {
                setCookieValue('qso_sat_qso', satQsoCheckbox.checked, 365);
            }

            const cookieFieldsToSave = qsoInputForm.querySelectorAll('.cookie-field');
            cookieFieldsToSave.forEach(field => {
                const cookieName = field.dataset.cookie;
                if (field.value) {
                    setCookieValue(cookieName, field.value);
                }
            });

            setCookieValue('qso_form_collapsed', 'false', 365);
        });
    }

    // Fix modal scroll issues
    document.body.style.overflow = 'visible';
    document.body.style.paddingRight = '0';
});

// ========== Chat ==========
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
let lastMessageId = null;

function loadChatMessages() {
    fetch('/dashboard/chat/list/')
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                const firstId = data.messages[0].id;
                if (lastMessageId !== firstId) {
                    renderMessages(data.messages);
                    lastMessageId = firstId;
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            } else if (chatMessages) {
                chatMessages.innerHTML = '<div class="text-center text-muted py-2">Нет сообщений</div>';
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки чата:', error);
        });
}

function renderMessages(messages) {
    if (!chatMessages) return;
    chatMessages.innerHTML = messages.map(msg => `
        <div class="chat-message">
            <div class="d-flex justify-content-between">
                <span class="username">${escapeHtml(msg.username)} (id=${msg.user_id})</span>
                <span class="time">${msg.created_at}</span>
            </div>
            <div class="text">${escapeHtml(msg.message)}</div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

if (chatForm) {
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        chatSendBtn.disabled = true;
        chatSendBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

        fetch('/dashboard/chat/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            chatSendBtn.disabled = false;
            chatSendBtn.innerHTML = '✈️';
            if (data.success) {
                chatInput.value = '';
                loadChatMessages();
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            chatSendBtn.disabled = false;
            chatSendBtn.innerHTML = '✈️';
            console.error('Ошибка отправки:', error);
            alert('Ошибка при отправке сообщения');
        });
    });
}

// Load chat on page load
document.addEventListener('DOMContentLoaded', function() {
    loadChatMessages();
    setInterval(loadChatMessages, 30000);
});

// ========== ADIF Upload ==========
function deleteAdifUpload(uploadId, fileName) {
    if (confirm('Удалить связанные QSO для файла "' + fileName + '"?')) {
        fetch('/dashboard/adif/delete/' + uploadId + '/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Ошибка при удалении');
        });
    }
}