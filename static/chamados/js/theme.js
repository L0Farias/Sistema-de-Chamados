// static/chamados/js/theme.js
// Dark Mode global — compartilhado por todas as páginas do sistema.
// Deve ser carregado em TODOS os templates que possuam o botão #darkModeToggle.

(function () {
    // Aplica o tema imediatamente (antes do DOMContentLoaded) para evitar flash branco
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark-mode-early');
        // A classe real é aplicada no body após o DOM carregar
    }
})();

document.addEventListener('DOMContentLoaded', function () {
    const body   = document.body;
    const toggle = document.getElementById('darkModeToggle');

    function applyTheme(isDark) {
        body.classList.toggle('dark-mode', isDark);
        document.documentElement.classList.remove('dark-mode-early');
        if (toggle) {
            toggle.innerHTML = isDark
                ? '<i class="fas fa-sun"></i>'
                : '<i class="fas fa-moon"></i>';
        }
    }

    // Restaura o tema salvo ao carregar a página
    applyTheme(localStorage.getItem('darkMode') === 'true');

    // Listener do botão de toggle
    if (toggle) {
        toggle.addEventListener('click', function () {
            const isDark = !body.classList.contains('dark-mode');
            applyTheme(isDark);
            localStorage.setItem('darkMode', String(isDark));
        });
    }
});
