/**
 * Скрипты для страницы рейтинга
 */

document.addEventListener('DOMContentLoaded', function() {
    // Навигация по вкладкам рейтинга
    const navButtons = document.querySelectorAll('.rating-nav-btn');
    const tabs = document.querySelectorAll('.rating-tab');

    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Убираем активный класс со всех кнопок
            navButtons.forEach(btn => btn.classList.remove('active'));
            // Добавляем активный класс на нажатую кнопку
            this.classList.add('active');

            // Получаем ID вкладки
            const tabId = this.getAttribute('data-tab') + '-tab';

            // Скрываем все вкладки
            tabs.forEach(tab => tab.classList.remove('active'));

            // Показываем нужную вкладку
            const activeTab = document.getElementById(tabId);
            if (activeTab) {
                activeTab.classList.add('active');
            }
        });
    });

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
