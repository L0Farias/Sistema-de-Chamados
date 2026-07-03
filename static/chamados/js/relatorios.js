// static/chamados/js/relatorios.js
// Exclusivo da página Relatórios — filtros, tabela AJAX, paginação, exportação Excel

let paginaAtual = 1;

function getFiltros() {
    return {
        etiqueta:  document.getElementById('fEtiqueta').value,
        status:    document.getElementById('fStatus').value,
        atendente: document.getElementById('fAtendente').value,
        data_ini:  document.getElementById('fDataIni').value,
        data_fim:  document.getElementById('fDataFim').value,
        busca:     document.getElementById('fBusca').value,
    };
}

function limparFiltros() {
    ['fEtiqueta','fStatus','fAtendente','fDataIni','fDataFim','fBusca']
        .forEach(id => { document.getElementById(id).value = ''; });
    buscar(1);
}

function buscar(pagina) {
    paginaAtual = pagina;
    const params = new URLSearchParams({...getFiltros(), page: pagina});
    fetch('/relatorios/ajax/?' + params)
        .then(r => r.json())
        .then(data => {
            renderTabela(data);
            renderPaginacao(data);
        })
        .catch(err => console.error('Erro ao buscar chamados:', err));
}

function etiquetaBadge(etiqueta) {
    const mapa = {
        'Problema':          'bg-warning text-dark',
        'Solicitação':       'bg-info text-dark',
        'Computador Locado': 'bg-primary',
        'Impressora Locada': 'bg-secondary',
        'Rede':              'bg-primary',
        'Computador':        'bg-secondary',
        'Telefone':          'bg-info text-dark',
    };
    if (!etiqueta || etiqueta === '—') return '<span class="text-muted">—</span>';
    const partes = etiqueta.split(', ');
    return partes.map(e => {
        const cls = mapa[e.trim()] || 'bg-dark';
        return `<span class="badge ${cls}">${e.trim()}</span>`;
    }).join(' ');
}

function statusBadge(status) {
    const mapa = {
        'Novo':           'bg-primary',
        'Triagem':        'bg-warning text-dark',
        'Em Atendimento': 'bg-info text-dark',
        'Fechado':        'bg-success',
    };
    const cls = mapa[status] || 'bg-secondary';
    return `<span class="badge ${cls}">${status}</span>`;
}

function renderTabela(data) {
    const tbody = document.getElementById('tabelaBody');
    const totalEl = document.getElementById('totalInfo');
    if (totalEl) totalEl.textContent = `${data.total} chamado(s) encontrado(s)`;
    if (!data.chamados || !data.chamados.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-4">Nenhum chamado encontrado.</td></tr>';
        return;
    }
    tbody.innerHTML = data.chamados.map(c => `
        <tr>
            <td><strong>#${c.id}</strong></td>
            <td>${c.solicitante}</td>
            <td>${c.local}</td>
            <td>${c.categoria}</td>
            <td>${etiquetaBadge(c.etiqueta)}</td>
            <td>${statusBadge(c.status)}</td>
            <td>${c.data_abertura}</td>
            <td>${c.data_fechamento}</td>
            <td>${c.atendente}</td>
        </tr>`).join('');
}

function renderPaginacao(data) {
    const div = document.getElementById('paginacao');
    if (!div) return;
    if (data.num_pages <= 1) { div.innerHTML = ''; return; }
    let html = '';
    if (data.has_prev)
        html += `<button class="btn btn-outline-secondary btn-sm" onclick="buscar(${data.page - 1})">‹ Anterior</button>`;
    html += `<span class="btn btn-sm disabled">Pág ${data.page} / ${data.num_pages}</span>`;
    if (data.has_next)
        html += `<button class="btn btn-outline-secondary btn-sm" onclick="buscar(${data.page + 1})">Próxima ›</button>`;
    div.innerHTML = html;
}

function exportarExcel() {
    const tipo = document.querySelector('input[name="tipoExport"]:checked').value;
    const params = tipo === 'filtrado' ? new URLSearchParams(getFiltros()).toString() : '';
    window.location.href = '/relatorios/exportar/?' + params;
    const modalEl = document.getElementById('modalExportar');
    if (modalEl) bootstrap.Modal.getInstance(modalEl)?.hide();
}

document.addEventListener('DOMContentLoaded', function () {
    buscar(1);
    const fBusca = document.getElementById('fBusca');
    if (fBusca) fBusca.addEventListener('keydown', e => { if (e.key === 'Enter') buscar(1); });
});
