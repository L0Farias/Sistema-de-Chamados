// static/chamados/js/dashboard.js
// Exclusivo da página Dashboard — KPIs e gráficos Chart.js

document.addEventListener('DOMContentLoaded', function () {

    fetch('/relatorios/dashboard/')
        .then(r => r.json())
        .then(data => {
            renderKPIs(data);
            renderCharts(data);
        })
        .catch(err => console.error('Erro ao carregar dashboard:', err));

    function renderKPIs(data) {
        // Os KPIs vêm do contexto Django (elementos já presentes no HTML)
        // Nada a fazer aqui além de garantir que os gráficos estão corretos
    }

    function renderCharts(data) {
        // Gráfico 1 — Por Etiqueta (doughnut)
        const ctxEtiqueta = document.getElementById('chartEtiqueta');
        if (ctxEtiqueta) {
            new Chart(ctxEtiqueta, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data.por_etiqueta),
                    datasets: [{
                        data: Object.values(data.por_etiqueta),
                        backgroundColor: [
                            '#f97316','#3b82f6','#22c55e',
                            '#8b5cf6','#6b7280','#92400e','#06b6d4'
                        ],
                    }]
                },
                options: {
                    plugins: { legend: { position: 'bottom', labels: { font: { size: 11 } } } },
                    maintainAspectRatio: false,
                }
            });
        }

        // Gráfico 2 — Por Status (bar)
        const ctxStatus = document.getElementById('chartStatus');
        if (ctxStatus) {
            new Chart(ctxStatus, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.por_status),
                    datasets: [{
                        label: 'Chamados',
                        data: Object.values(data.por_status),
                        backgroundColor: ['#3b82f6','#f97316','#06b6d4','#22c55e'],
                        borderRadius: 5,
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
                    maintainAspectRatio: false,
                }
            });
        }

        // Gráfico 3 — Por Atendente (bar horizontal)
        const ctxAtendente = document.getElementById('chartAtendente');
        if (ctxAtendente) {
            new Chart(ctxAtendente, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.por_atendente),
                    datasets: [{
                        label: 'Chamados',
                        data: Object.values(data.por_atendente),
                        backgroundColor: '#6366f1',
                        borderRadius: 5,
                    }]
                },
                options: {
                    indexAxis: 'y',
                    plugins: { legend: { display: false } },
                    scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } },
                    maintainAspectRatio: false,
                }
            });
        }
    }
});
