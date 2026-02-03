// Исправление для мобильного меню
document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы мобильного меню
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Инициализируем Bootstrap collapse
        const collapse = new bootstrap.Collapse(navbarCollapse, {
            toggle: false
        });
        
        // Обработчик клика по кнопке
        navbarToggler.addEventListener('click', function() {
            if (navbarCollapse.classList.contains('show')) {
                collapse.hide();
            } else {
                collapse.show();
            }
        });
        
        // Закрываем меню при клике на ссылку
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                collapse.hide();
            });
        });
        
        // Закрываем меню при изменении размера окна
        window.addEventListener('resize', function() {
            if (window.innerWidth > 991) {
                collapse.hide();
            }
        });
    }
});