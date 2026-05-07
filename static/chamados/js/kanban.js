
document.addEventListener('DOMContentLoaded', function() {

    const toggle = document.getElementById('darkModeToggle');
    const body = document.body;

    function applyTheme(isDark) {
        if (isDark) {
            body.classList.add('dark-mode');
            if (toggle) toggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            body.classList.remove('dark-mode');
            if (toggle) toggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    // ==================== ABRIR MODAL AO CLICAR NO CARD ====================
    document.querySelectorAll('.kanban-card').forEach(card => {
        card.addEventListener('click', function() {
            const chamadoId = this.getAttribute('data-id');
            abrirModalChamado(chamadoId);
        });
    });

    // ==================== ABRIR MODAL ====================
    window.abrirModalChamado = function(chamadoId) {
        const modalElement = document.getElementById('detalheModal');
        const modal = new bootstrap.Modal(modalElement);
        
        document.getElementById('modalId').textContent = chamadoId;
        
        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-3">Carregando detalhes do chamado #${chamadoId}...</p>
            </div>
        `;

        modal.show();

        // Simulação de carregamento (futuramente vamos buscar dados reais)
        setTimeout(() => {
            modalBody.innerHTML = `
                <h5 class="mb-3">Detalhes do Chamado #${chamadoId}</h5>
                <p><strong>Esta funcionalidade está em desenvolvimento.</strong></p>
                <p>Aqui aparecerão:</p>
                <ul>
                    <li>Descrição completa do problema</li>
                    <li>Histórico de mensagens (chat)</li>
                    <li>Status atual e atendente</li>
                    <li>Botões de ação (Triar, Iniciar Atendimento, Fechar)</li>
                </ul>
            `;
        }, 600);
    };
    }

    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'true') {
        applyTheme(true);
    }

    // Dark Mode
    if (toggle) {
        toggle.addEventListener('click', () => {
            const isDark = !body.classList.contains('dark-mode');
            applyTheme(isDark);
            localStorage.setItem('darkMode', isDark);
        });
    }

    // ==AJAX
    document.querySelectorAll('.cards-container').forEach(container => {
        let page = 2;
        const status = container.dataset.status;

        container.addEventListener('scroll', () => {
            if (container.scrollTop + container.clientHeight >= container.scrollHeight - 80) {
                loadMoreChamados(container, status, page);
                page++;
            }
        });
    });

    function loadMoreChamados(container, status, page) {
        fetch(`/load-more-chamados/?status=${status}&page=${page}`)
            .then(response => response.json())
            .then(data => {
                if (data.chamados && data.chamados.length > 0) {
                    data.chamados.forEach(chamado => {
                        const cardHTML = `
                            <a href="/chamado/${chamado.id}/" class="text-decoration-none">
                                <div class="kanban-card">
                                    <strong>#${chamado.id}</strong><br>
                                    ${chamado.nome_usuario}<br>
                                    <small>${chamado.local} • ${chamado.categoria}</small>
                                </div>
                            </a>`;
                        container.innerHTML += cardHTML;
                    });
                }
            })
            .catch(error => console.error('Erro ao carregar mais chamados:', error));
    }
});