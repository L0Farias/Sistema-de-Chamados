// static/chamados/js/agendamento.js
// Validações do formulário de Agendamento de Multimídia

document.addEventListener('DOMContentLoaded', function () {
    const form        = document.getElementById('formAgendamento');
    const fData       = document.getElementById('id_data');
    const fInicio     = document.getElementById('id_horario_inicio');
    const fFim        = document.getElementById('id_horario_fim');

    // Define data mínima como hoje
    if (fData) {
        const hoje = new Date().toISOString().split('T')[0];
        fData.setAttribute('min', hoje);
    }

    if (form) {
        form.addEventListener('submit', function (e) {
            let valido = true;
            const msgs = [];

            // Data não pode ser anterior a hoje
            if (fData && fData.value) {
                const hoje = new Date().toISOString().split('T')[0];
                if (fData.value < hoje) {
                    msgs.push('A data não pode ser anterior a hoje.');
                    valido = false;
                }
            }

            // Horário de fim deve ser posterior ao início
            if (fInicio && fFim && fInicio.value && fFim.value) {
                if (fFim.value <= fInicio.value) {
                    msgs.push('O horário de fim deve ser posterior ao horário de início.');
                    valido = false;
                }
            }

            // Ao menos um equipamento deve ser marcado
            const checkboxes = form.querySelectorAll('input[name="equipamentos"]:checked');
            if (checkboxes.length === 0) {
                msgs.push('Selecione ao menos um equipamento.');
                valido = false;
            }

            if (!valido) {
                e.preventDefault();
                let alertEl = document.getElementById('agendamento-erros');
                if (!alertEl) {
                    alertEl = document.createElement('div');
                    alertEl.id = 'agendamento-erros';
                    alertEl.className = 'alert alert-danger mt-2';
                    form.prepend(alertEl);
                }
                alertEl.innerHTML = msgs.map(m => `<div>• ${m}</div>`).join('');
                alertEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }
});
