/**
 * Скрипты для страницы рейтинга
 */

document.addEventListener('DOMContentLoaded', function() {
    const navButtons = document.querySelectorAll('.rating-nav-btn');
    const tabs = document.querySelectorAll('.rating-tab');
    const activeTabInput = document.getElementById('active-tab');

    // Получаем активную вкладку из URL параметра или из скрытого поля
    const urlParams = new URLSearchParams(window.location.search);
    const activeTabFromUrl = urlParams.get('active_tab');
    const initialActiveTab = activeTabFromUrl || activeTabInput.value || 'regions';

    // Устанавливаем активную вкладку при загрузке
    setActiveTab(initialActiveTab);

    // Навигация по вкладкам рейтинга
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            setActiveTab(tabId);
        });
    });

    // Функция для установки активной вкладки
    function setActiveTab(tabId) {
        // Обновляем скрытое поле
        if (activeTabInput) {
            activeTabInput.value = tabId;
        }

        // Убираем активный класс со всех кнопок
        navButtons.forEach(btn => btn.classList.remove('active'));
        // Добавляем активный класс на соответствующую кнопку
        const activeButton = document.querySelector(`.rating-nav-btn[data-tab="${tabId}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }

        // Скрываем все вкладки
        tabs.forEach(tab => tab.classList.remove('active'));

        // Показываем нужную вкладку
        const activeTab = document.getElementById(tabId + '-tab');
        if (activeTab) {
            activeTab.classList.add('active');
        }
    }

    // Автоматическая отправка формы при изменении фильтров
    const filterRadios = document.querySelectorAll('.filter-radio');
    const filterForm = document.getElementById('rating-filter-form');

    filterRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (filterForm) {
                filterForm.submit();
            }
        });
    });
});
