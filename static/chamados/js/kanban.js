// static/chamados/js/kanban.js

// Lê o CSRF token do cookie (necessário para requisições POST)
function getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        const trimmed = c.trim();
        if (trimmed.startsWith(name + '=')) {
            return decodeURIComponent(trimmed.slice(name.length + 1));
        }
    }
    return '';
}

// Envia ação POST para uma URL de transição de status
function executarAcao(url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        credentials: 'same-origin',
    })
    .then(response => {
        // Considera sucesso se respondeu 200 ou fez redirect (302 seguido pelo fetch)
        // Verifica que não foi redirecionado para a tela de login
        if ((response.ok || response.redirected) && !response.url.includes('/login/')) {
            const modalEl = document.getElementById('detalheModal');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) modalInstance.hide();
            window.location.reload();
        } else if (response.url.includes('/login/')) {
            alert('Sessão expirada. Faça login novamente.');
            window.location.href = '/login/';
        } else {
            alert('Erro ao executar ação. Tente novamente.');
        }
    })
    .catch(() => alert('Erro de conexão. Tente novamente.'));
}

// Retorna os botões de ação conforme o status atual do chamado
function renderizarBotoes(status, chamadoId) {
    const acoes = {
        'Novo': [
            { label: 'Iniciar Atendimento', url: `/chamado/${chamadoId}/iniciar/`, cls: 'btn-success'  },
        ],
        'Triagem': [
            { label: 'Iniciar Atendimento', url: `/chamado/${chamadoId}/iniciar/`, cls: 'btn-success'  },
        ],
        'Em Atendimento': [
            { label: 'Fechar Chamado',      url: `/chamado/${chamadoId}/fechar/`,  cls: 'btn-danger'   },
        ],
        'Fechado': [
            { label: 'Reabrir',             url: `/chamado/${chamadoId}/reabrir/`, cls: 'btn-secondary'},
        ],
    };

    const botoes = acoes[status] || [];
    if (botoes.length === 0) return '<span class="text-muted small">Nenhuma ação disponível.</span>';

    return botoes.map(b =>
        `<button class="btn ${b.cls} btn-sm" onclick="executarAcao('${b.url}')">${b.label}</button>`
    ).join('');
}

document.addEventListener('DOMContentLoaded', function() {

    // Dark Mode
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
    }

    if (localStorage.getItem('darkMode') === 'true') {
        applyTheme(true);
    }

    if (toggle) {
        toggle.addEventListener('click', () => {
            const isDark = !body.classList.contains('dark-mode');
            applyTheme(isDark);
            localStorage.setItem('darkMode', isDark);
        });
    }

    // Abrir Modal
    document.querySelectorAll('.kanban-card').forEach(card => {
        card.addEventListener('click', function() {
            const chamadoId = this.getAttribute('data-id');
            if (chamadoId) {
                abrirModalChamado(chamadoId);
            }
        });
    });
});

window.abrirModalChamado = function(chamadoId) {
    const modal = new bootstrap.Modal(document.getElementById('detalheModal'));
    const modalBody = document.getElementById('modalBody');

    document.getElementById('modalId').textContent = chamadoId;

    // Estrutura inicial com placeholder de carregamento nas ações
    modalBody.innerHTML = `
        <div class="row g-4">
            <!-- Coluna Lateral Esquerda - Informações -->
            <div class="col-lg-4 border-end">
                <h6 class="text-primary mb-3">📋 Informações</h6>
                <table class="table table-borderless table-sm">
                    <tr><th>Solicitante</th><td id="modalSolicitante" class="text-end"></td></tr>
                    <tr><th>Local</th><td id="modalLocal" class="text-end"></td></tr>
                    <tr><th>Categoria</th><td id="modalCategoria" class="text-end"></td></tr>
                    <tr><th>Tipo</th><td id="modalTipo" class="text-end"></td></tr>
                    <tr><th>Status</th><td id="modalStatus" class="text-end"></td></tr>
                    <tr><th>Data Abertura</th><td id="modalData" class="text-end"></td></tr>
                    <tr><th>Atendente</th><td id="modalAtendente" class="text-end"></td></tr>
                </table>
            </div>

            <!-- Coluna Principal - Descrição e Ações -->
            <div class="col-lg-8">
                <h6 class="text-primary mb-3">📝 Descrição do Problema</h6>
                <div class="border p-4 rounded-3 bg-light modal-descricao mb-4" style="min-height: 180px;">
                    <p id="modalDescricao" class="mb-0"></p>
                </div>

                <h6 class="text-primary mb-3">⚡ Ações Rápidas</h6>
                <div id="modalAcoes" class="d-flex flex-wrap gap-2">
                    <span class="text-muted small">Carregando...</span>
                </div>
            </div>
        </div>
    `;

    modal.show();

    // Carregar dados reais e renderizar botões com base no status
    fetch(`/chamado/${chamadoId}/ajax/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('modalDescricao').textContent = data.problema || 'Sem descrição.';
            document.getElementById('modalSolicitante').textContent = data.nome_usuario;
            document.getElementById('modalLocal').textContent = data.local;
            document.getElementById('modalCategoria').textContent = data.categoria;
            document.getElementById('modalTipo').textContent = data.tipo;
            document.getElementById('modalStatus').innerHTML = `<span class="badge bg-info">${data.status}</span>`;
            document.getElementById('modalData').textContent = data.data_abertura;
            document.getElementById('modalAtendente').textContent = data.atendente;

            // Renderiza botões funcionais com base no status real
            document.getElementById('modalAcoes').innerHTML = renderizarBotoes(data.status, chamadoId);
        })
        .catch(() => {
            document.getElementById('modalAcoes').innerHTML =
                '<span class="text-danger small">Erro ao carregar ações.</span>';
        });
};