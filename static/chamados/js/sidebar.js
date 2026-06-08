// static/chamados/js/sidebar.js

document.addEventListener('DOMContentLoaded', function() {

    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');

    function updateToggleIcon(isCollapsed) {
        if (!toggleBtn) return;
        const icon = toggleBtn.querySelector('i');
        if (!icon) return;
        if (isCollapsed) {
            icon.classList.replace('fa-chevron-left', 'fa-chevron-right');
            icon.classList.replace('fa-bars', 'fa-chevron-right');
        } else {
            icon.classList.replace('fa-chevron-right', 'fa-chevron-left');
            icon.classList.replace('fa-bars', 'fa-chevron-left');
        }
    }

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');

            // Opcional: salvar preferência
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
            updateToggleIcon(isCollapsed);
        });

        // Restaurar estado salvo
        if (localStorage.getItem('sidebarCollapsed') === 'true') {
            sidebar.classList.add('collapsed');
            updateToggleIcon(true);
        } else {
            updateToggleIcon(false);
        }
    }
});