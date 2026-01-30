// Cosmos Diploma JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('callsigns-container');

    // Инициализация обработчиков для существующих полей ввода позывных
    initCallsignInputs();

    // Делегирование событий для кнопок удаления
    container.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-remove-callsign') ||
            e.target.parentElement.classList.contains('btn-remove-callsign')) {
            const button = e.target.classList.contains('btn-remove-callsign') ? e.target : e.target.parentElement;
            const item = button.closest('.my-callsign-item');

            // Всегда удаляем элемент
            item.remove();

            // Если элементов не осталось, добавляем новый пустой
            const remainingItems = container.querySelectorAll('.my-callsign-item');
            if (remainingItems.length === 0) {
                addCallsign();
            }
        }
    });

    // Формирование JSON перед отправкой формы
    document.getElementById('cosmosForm').addEventListener('submit', function() {
        const callsigns = [];
        const items = container.querySelectorAll('.my-callsign-item');

        items.forEach(item => {
            const input = item.querySelector('input[name="other_callsigns_names[]"]');
            const name = input.value.trim().toUpperCase();
            if (name) {
                callsigns.push(name);
            }
        });

        document.getElementById('other_callsigns_json').value = JSON.stringify(callsigns);
    });
});

// Добавление нового позывного
function addCallsign() {
    const container = document.getElementById('callsigns-container');
    const item = document.createElement('div');
    item.className = 'my-callsign-item';
    item.innerHTML = `
        <input type="text" class="form-control callsign-input"
               name="other_callsigns_names[]"
               placeholder="Позывной"
               autocomplete="off">
        <button type="button" class="btn btn-outline-danger btn-sm btn-remove-callsign">
            ✕
        </button>
    `;
    container.appendChild(item);

    // Добавляем обработчик для автоматического перевода в верхний регистр
    const callsignInput = item.querySelector('.callsign-input');
    callsignInput.addEventListener('input', function() {
        this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
    });
}

// Инициализация обработчиков для полей ввода позывных
function initCallsignInputs() {
    document.querySelectorAll('.callsign-input').forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9\/]/g, '');
        });
    });
}