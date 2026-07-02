// static/chamados/js/kanban.js  –  Sistema de Chamados TICS

// ─── Utilitários ──────────────────────────────────────────────────────────────

function getCsrfToken() {
    const name = 'csrftoken';
    for (const c of document.cookie.split(';')) {
        const t = c.trim();
        if (t.startsWith(name + '='))
            return decodeURIComponent(t.slice(name.length + 1));
    }
    return '';
}

/** Calcula luminância relativa (#RRGGBB) e retorna '#fff' ou '#000' */
function corTexto(hex) {
    const r = parseInt(hex.slice(1,3),16) / 255;
    const g = parseInt(hex.slice(3,5),16) / 255;
    const b = parseInt(hex.slice(5,7),16) / 255;
    const lum = 0.2126*r + 0.7152*g + 0.0722*b;
    return lum > 0.45 ? '#000' : '#fff';
}

/** Gera HTML de um badge de etiqueta com cor inline */
function badgeEtiqueta(nome, cor) {
    const txt = corTexto(cor);
    return `<span class="badge-etiqueta"
        style="background:${cor};color:${txt};padding:3px 10px;border-radius:20px;
               font-size:.75rem;font-weight:600;">${nome}</span>`;
}

/** Retorna badge de status com classe Bootstrap */
function badgeStatus(status) {
    const mapa = {
        'Novo':           'bg-primary',
        'Triagem':        'bg-warning text-dark',
        'Em Atendimento': 'bg-info text-dark',
        'Fechado':        'bg-success',
    };
    return `<span class="badge rounded-pill ${mapa[status] || 'bg-secondary'}">${status}</span>`;
}

// ─── Ação POST (transição de status) ─────────────────────────────────────────

function executarAcao(url) {
    fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken(),
                   'Content-Type': 'application/x-www-form-urlencoded' },
        credentials: 'same-origin',
    })
    .then(res => {
        if ((res.ok || res.redirected) && !res.url.includes('/login/')) {
            const inst = bootstrap.Modal.getInstance(document.getElementById('detalheModal'));
            if (inst) inst.hide();
            window.location.reload();
        } else if (res.url.includes('/login/')) {
            alert('Sessão expirada. Faça login novamente.');
            window.location.href = '/login/';
        } else {
            alert('Erro ao executar ação. Tente novamente.');
        }
    })
    .catch(() => alert('Erro de conexão. Tente novamente.'));
}

// ─── Botões de ação por status ────────────────────────────────────────────────

function renderizarBotoes(status, chamadoId) {
    const acoes = {
        'Novo':           [{ label:'Iniciar Atendimento', url:`/chamado/${chamadoId}/iniciar/`, cls:'btn-success' }],
        'Triagem':        [{ label:'Iniciar Atendimento', url:`/chamado/${chamadoId}/iniciar/`, cls:'btn-success' }],
        'Em Atendimento': [{ label:'Fechar Chamado',      url:`/chamado/${chamadoId}/fechar/`,  cls:'btn-danger'  },
                           { label:'Reabrir',             url:`/chamado/${chamadoId}/reabrir/`, cls:'btn-secondary'}],
        'Fechado':        [{ label:'Reabrir',             url:`/chamado/${chamadoId}/reabrir/`, cls:'btn-secondary'}],
    };
    const botoes = acoes[status] || [];
    if (!botoes.length) return '<span class="text-muted small">Nenhuma ação disponível.</span>';
    return botoes.map(b =>
        `<button class="btn ${b.cls} btn-sm w-100" onclick="executarAcao('${b.url}')">${b.label}</button>`
    ).join('');
}

// ─── Salvar etiquetas (M2M) ───────────────────────────────────────────────────

function salvarEtiquetas(chamadoId) {
    const checks = document.querySelectorAll('#listaEtiquetasCheck input[type=checkbox]:checked');
    const ids = Array.from(checks).map(cb => parseInt(cb.value));

    fetch(`/chamado/${chamadoId}/etiquetas/salvar/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify({ etiqueta_ids: ids }),
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) { alert('Erro ao salvar etiquetas.'); return; }

        // 1. Atualizar badges no topo do modal
        const badgesArea = document.getElementById('modalBadgesEtiqueta');
        if (badgesArea) {
            badgesArea.innerHTML = data.etiquetas.length
                ? data.etiquetas.map(e => badgeEtiqueta(e.nome, e.cor)).join(' ')
                : '<span class="text-muted small">Sem etiqueta</span>';
        }

        // 2. Atualizar timeline com histórico retornado pelo servidor
        const hist = document.getElementById('timelineHistorico');
        if (hist && data.historico_etiquetas !== undefined) {
            // Adiciona apenas os eventos de etiqueta ao histórico existente
            // buscando os dados completos do chamado para montar a timeline
            fetch(`/chamado/${chamadoId}/ajax/`)
                .then(r => r.json())
                .then(d => { hist.innerHTML = renderizarHistorico(d); });
        }

        // 3. Atualizar a área de etiquetas do card do Kanban sem reload
        const card = document.querySelector(`.kanban-card[data-id="${chamadoId}"]`);
        if (card) {
            let badgeArea = card.querySelector('.card-etiquetas-area');
            if (!badgeArea) {
                badgeArea = document.createElement('div');
                badgeArea.className = 'card-etiquetas-area d-flex flex-wrap gap-1 mb-2';
                const dataEl = card.querySelector('small');
                if (dataEl) card.insertBefore(badgeArea, dataEl);
                else card.appendChild(badgeArea);
            }
            if (data.etiquetas.length) {
                badgeArea.innerHTML = data.etiquetas.map(e => {
                    const txt = corTexto(e.cor);
                    return `<span class="badge-etiqueta kanban-badge-et" data-cor="${e.cor}"
                        style="background:${e.cor};color:${txt};">${e.nome}</span>`;
                }).join('');
            } else {
                badgeArea.innerHTML = '';
            }
        }
    })
    .catch(() => alert('Erro de conexão ao salvar etiquetas.'));
}

function limparEtiquetas(chamadoId) {
    // Desmarca todos os checkboxes e salva
    document.querySelectorAll('#listaEtiquetasCheck input[type=checkbox]')
        .forEach(cb => cb.checked = false);
    salvarEtiquetas(chamadoId);
}

// ─── Renderizadores parciais ──────────────────────────────────────────────────

/** Uma linha do grid de informações */
function infoRow(label, value) {
    const v = (value !== null && value !== undefined && value !== '') ? value : '—';
    return `
    <div class="info-grid-row">
        <span class="info-grid-label">${label}</span>
        <span class="info-grid-value">${v}</span>
    </div>`;
}

/** Monta a seção de informações em duas colunas (grid) */
function renderizarInformacoes(dados) {
    return `
    <div class="info-grid-2col">
        <div class="info-grid-col">
            ${infoRow('Solicitante', dados.nome_usuario)}
            ${infoRow('Local',       dados.local)}
            ${infoRow('Categoria',   dados.categoria)}
        </div>
        <div class="info-grid-col">
            ${infoRow('Tipo',        dados.tipo)}
            ${infoRow('Abertura',    dados.data_abertura)}
            ${infoRow('Atendente',   dados.atendente)}
            ${dados.data_fechamento ? infoRow('Fechamento', dados.data_fechamento) : ''}
        </div>
    </div>`;
}

function renderizarHistorico(data) {
    let html = '';

    // Criação
    html += `
    <div class="timeline-item">
        <div class="d-flex align-items-center gap-2 mb-1">
            <span class="timeline-icon">🕒</span>
            <span class="timeline-title">Chamado criado</span>
        </div>
        <div class="timeline-date">${data.data_abertura}</div>
    </div>`;

    // Atendimento iniciado
    if (data.atendente && data.status !== 'Novo' && data.status !== 'Triagem') {
        html += `
    <div class="timeline-item">
        <div class="d-flex align-items-center gap-2 mb-1">
            <span class="timeline-icon">👤</span>
            <span class="timeline-title">Atendimento iniciado</span>
        </div>
        <div class="timeline-sub">${data.atendente}</div>
    </div>`;
    }

    // Reabertura
    if (data.data_reabertura) {
        html += `
    <div class="timeline-item" style="border-left-color:#f59e0b">
        <div class="d-flex align-items-center gap-2 mb-1">
            <span class="timeline-icon">🔄</span>
            <span class="timeline-title">Chamado reaberto</span>
        </div>
        ${data.reaberto_por ? `<div class="timeline-sub">Por: ${data.reaberto_por}</div>` : ''}
        <div class="timeline-date">${data.data_reabertura}</div>
    </div>`;
    }

    // Fechamento
    if (data.data_fechamento) {
        html += `
    <div class="timeline-item" style="border-left-color:#22c55e">
        <div class="d-flex align-items-center gap-2 mb-1">
            <span class="timeline-icon">✅</span>
            <span class="timeline-title">Chamado fechado</span>
        </div>
        ${data.atendente_fechamento ? `<div class="timeline-sub">${data.atendente_fechamento}</div>` : ''}
        <div class="timeline-date">${data.data_fechamento}</div>
    </div>`;
    }

    // Histórico de etiquetas — agrupa eventos do mesmo usuário/data próximos
    if (data.historico_etiquetas && data.historico_etiquetas.length) {
        // Agrupar: eventos consecutivos do mesmo usuário+acao com mesma data (minuto)
        const grupos = [];
        for (const h of data.historico_etiquetas) {
            const chave = `${h.usuario}|${h.acao}|${h.data}`;
            const ultimo = grupos[grupos.length - 1];
            if (ultimo && ultimo.chave === chave) {
                ultimo.etiquetas.push({ nome: h.etiqueta, cor: h.cor });
            } else {
                grupos.push({ chave, usuario: h.usuario, acao: h.acao, data: h.data,
                              etiquetas: [{ nome: h.etiqueta, cor: h.cor }] });
            }
        }

        for (const g of grupos) {
            const icone  = g.acao === 'adicionada' ? '🏷' : '🗑';
            const verbo  = g.acao === 'adicionada' ? 'adicionou' : 'removeu';
            const plural = g.etiquetas.length > 1;
            const titulo = plural
                ? `${g.usuario} ${verbo} as etiquetas`
                : `${g.usuario} ${verbo} a etiqueta`;
            const badgesHtml = g.etiquetas.map(e => badgeEtiqueta(e.nome, e.cor)).join(' ');
            const cor = g.etiquetas[0].cor;
            html += `
    <div class="timeline-item" style="border-left-color:${cor}">
        <div class="d-flex align-items-center gap-2 mb-1">
            <span class="timeline-icon">${icone}</span>
            <span class="timeline-title">${titulo}</span>
        </div>
        <div class="d-flex flex-wrap gap-1 my-1">${badgesHtml}</div>
        <div class="timeline-date">${g.data}</div>
    </div>`;
        }
    }

    if (!html) html = '<p class="text-muted small mb-0">Nenhum evento registrado.</p>';
    return html;
}

function renderizarCheckboxEtiquetas(todas, selecionadas) {
    if (!todas.length)
        return '<p class="text-muted small mb-0">Nenhuma etiqueta cadastrada.</p>';

    return todas.map(e => {
        const checked = selecionadas.includes(e.id) ? 'checked' : '';
        const txt = corTexto(e.cor);
        return `
    <label class="etiqueta-checkbox-item">
        <input type="checkbox" value="${e.id}" ${checked} style="accent-color:${e.cor};">
        <span class="etiqueta-dot" style="background:${e.cor};"></span>
        <span style="font-size:.88rem;">${e.nome}</span>
    </label>`;
    }).join('');
}

// ─── Modal principal ──────────────────────────────────────────────────────────

window.abrirModalChamado = function(chamadoId) {
    const modalEl   = document.getElementById('detalheModal');
    const modal     = new bootstrap.Modal(modalEl);
    const modalBody = document.getElementById('modalBody');

    document.getElementById('modalId').textContent = chamadoId;

    // Esqueleto imediato — evita flash vazio
    modalBody.innerHTML = `
<div class="container-fluid px-3 py-2">

    <!-- badges topo -->
    <div class="d-flex align-items-center gap-2 flex-wrap mb-3">
        <span id="modalBadgesEtiqueta" class="d-flex gap-1 flex-wrap">
            <span class="text-muted small">Carregando...</span>
        </span>
        <span id="modalBadgeStatus"></span>
    </div>

    <div class="row g-3">

        <!-- ── COLUNA PRINCIPAL ── -->
        <div class="col-12 col-lg-8">

            <!-- Informações -->
            <div class="card shadow-sm mb-3">
                <div class="card-header fw-semibold">📋 Informações</div>
                <div class="card-body" id="modalInfos">
                    <div class="text-muted small">Carregando...</div>
                </div>
            </div>

            <!-- Descrição -->
            <div class="card shadow-sm mb-3">
                <div class="card-header fw-semibold">📝 Descrição</div>
                <div class="card-body">
                    <p id="modalDescricao" class="mb-0 small" style="white-space:pre-wrap;line-height:1.6;"></p>
                </div>
            </div>

            <!-- Histórico -->
            <div class="card shadow-sm">
                <div class="card-header fw-semibold">🕒 Histórico</div>
                <div class="card-body p-2" id="timelineHistorico">
                    <div class="text-muted small p-2">Carregando...</div>
                </div>
            </div>

        </div>

        <!-- ── COLUNA LATERAL ── -->
        <div class="col-12 col-lg-4">

            <!-- Etiquetas -->
            <div class="card shadow-sm mb-3">
                <div class="card-header fw-semibold">🏷 Etiquetas</div>
                <div class="card-body">
                    <div id="listaEtiquetasCheck" class="etiqueta-checkbox-list mb-3">
                        <div class="text-muted small">Carregando...</div>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-secondary btn-sm flex-fill"
                                onclick="limparEtiquetas(${chamadoId})">
                            Limpar
                        </button>
                        <button class="btn btn-primary btn-sm flex-fill"
                                onclick="salvarEtiquetas(${chamadoId})">
                            Salvar
                        </button>
                    </div>
                </div>
            </div>

            <!-- Ações -->
            <div class="card shadow-sm">
                <div class="card-header fw-semibold">⚡ Ações</div>
                <div class="card-body">
                    <div id="modalAcoes" class="d-grid gap-2">
                        <div class="text-muted small">Carregando...</div>
                    </div>
                </div>
            </div>

        </div>

    </div>
</div>`;

    modal.show();

    // ── Carregar dados do chamado e etiquetas em paralelo ──────────────────
    Promise.all([
        fetch(`/chamado/${chamadoId}/ajax/`).then(r => r.json()),
        fetch(`/chamado/${chamadoId}/etiquetas/`).then(r => r.json()),
    ])
    .then(([dados, etData]) => {

        // Badges topo
        const badgesArea = document.getElementById('modalBadgesEtiqueta');
        badgesArea.innerHTML = dados.etiquetas && dados.etiquetas.length
            ? dados.etiquetas.map(e => badgeEtiqueta(e.nome, e.cor)).join(' ')
            : '<span class="text-muted small">Sem etiqueta</span>';

        document.getElementById('modalBadgeStatus').innerHTML = badgeStatus(dados.status);

        // Informações (grid 2 colunas)
        document.getElementById('modalInfos').innerHTML = renderizarInformacoes(dados);

        // Descrição
        document.getElementById('modalDescricao').textContent = dados.problema || '—';

        // Histórico
        document.getElementById('timelineHistorico').innerHTML = renderizarHistorico(dados);

        // Checkboxes de etiquetas
        document.getElementById('listaEtiquetasCheck').innerHTML =
            renderizarCheckboxEtiquetas(etData.todas || [], etData.selecionadas || []);

        // Botões de ação
        document.getElementById('modalAcoes').innerHTML = renderizarBotoes(dados.status, chamadoId);
    })
    .catch(err => {
        console.error('Erro ao carregar modal:', err);
        const acoesEl = document.getElementById('modalAcoes');
        if (acoesEl) acoesEl.innerHTML = '<span class="text-danger small">Erro ao carregar dados.</span>';
    });
};

// ─── Dark Mode ────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('darkModeToggle');
    const body   = document.body;

    function applyTheme(isDark) {
        body.classList.toggle('dark-mode', isDark);
        if (toggle) toggle.innerHTML = isDark
            ? '<i class="fas fa-sun"></i>'
            : '<i class="fas fa-moon"></i>';
    }

    applyTheme(localStorage.getItem('darkMode') === 'true');

    if (toggle) {
        toggle.addEventListener('click', () => {
            const isDark = !body.classList.contains('dark-mode');
            applyTheme(isDark);
            localStorage.setItem('darkMode', isDark);
        });
    }

    // Aplicar cor de texto com contraste correto nos badges dos cards (renderizados pelo Django)
    aplicarContrasteBadgesCards();

    // Abrir modal ao clicar em card
    document.querySelectorAll('.kanban-card').forEach(card => {
        card.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            if (id) abrirModalChamado(id);
        });
    });
});

/** Aplica cor de texto com contraste em todos os .kanban-badge-et da página */
function aplicarContrasteBadgesCards() {
    document.querySelectorAll('.kanban-badge-et').forEach(span => {
        const cor = span.getAttribute('data-cor') || span.style.background;
        if (cor) span.style.color = corTexto(cor);
    });
}
