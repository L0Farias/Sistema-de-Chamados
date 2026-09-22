# Documento de Requisitos

## Introdução

Esta feature realiza a reestruturação modular do sistema TICS (Django 5.2, Bootstrap 5, SQLite), reorganizando a interface da equipe de TI em cinco módulos distintos na sidebar — Kanban, Dashboard, Relatórios, Agendamento de Multimídia e Configurações — e adicionando o módulo de Agendamento de Multimídia para usuários comuns e técnicos de TI. O objetivo é reorganizar sem reescrever: máximo reaproveitamento do código existente, separação clara de responsabilidades por módulo e isolamento de scripts JS por página.

## Glossário

- **Sistema**: O sistema de chamados TICS (Django 5.2)
- **Sidebar**: Menu lateral de navegação presente nas páginas da equipe TI
- **Dashboard**: Página gerencial com KPIs, indicadores e gráficos (Chart.js) dos chamados
- **Relatórios**: Página de consulta e histórico com tabela paginada, filtros e exportação Excel
- **Agendamento**: Módulo para reserva de equipamentos multimídia (projetores, notebooks, etc.)
- **Agendamento_Multimidia**: Novo model Django que representa uma reserva de equipamentos multimídia
- **Equipe_TI**: Usuários com `tipo == 'ti'` no model `Usuario`
- **Usuario_Comum**: Usuários com `tipo == 'comum'` no model `Usuario`
- **Kanban**: Visualização de chamados por colunas de status (já existente, não alterado)
- **endpoint_dashboard**: Endpoint JSON existente em `/relatorios/dashboard/` que retorna dados para gráficos
- **dashboard_js**: Novo arquivo `static/chamados/js/dashboard.js` — exclusivo para gráficos/indicadores
- **relatorios_js**: Novo arquivo `static/chamados/js/relatorios.js` — filtros, paginação, exportação
- **agendamento_js**: Novo arquivo `static/chamados/js/agendamento.js` — validações do formulário de agendamento
- **kanban_js**: Arquivo existente `static/chamados/js/kanban.js` — exclusivo do Kanban (não alterado)

---

## Requisitos

### Requisito 1 — Nova Estrutura da Sidebar (5 Módulos)

**User Story:** Como membro da Equipe_TI, quero uma sidebar com cinco módulos distintos, para navegar de forma organizada entre as funcionalidades do sistema.

#### Critérios de Aceitação

1. THE Sistema SHALL exibir na sidebar os seguintes cinco itens de navegação, nesta ordem: Kanban, Dashboard, Relatórios, Agendamento de Multimídia e Configurações.
2. WHEN a Equipe_TI acessa qualquer página do sistema, THE Sistema SHALL destacar visualmente o item de navegação correspondente à página atual como ativo.
3. WHEN a Equipe_TI clica em "Kanban", THE Sistema SHALL navegar para a URL `/equipe-ti/`.
4. WHEN a Equipe_TI clica em "Dashboard", THE Sistema SHALL navegar para a URL `/dashboard/`.
5. WHEN a Equipe_TI clica em "Relatórios", THE Sistema SHALL navegar para a URL `/relatorios/`.
6. WHEN a Equipe_TI clica em "Agendamento de Multimídia", THE Sistema SHALL navegar para a URL `/agendamento-multimidia/`.
7. WHEN a Equipe_TI clica em "Configurações", THE Sistema SHALL exibir a página sem retornar erro HTTP (placeholder funcional).
8. THE Sistema SHALL reutilizar a estrutura de sidebar existente em `equipe_ti.html` (colapsável, dark theme, botões inferiores) sem duplicação de CSS.

---

### Requisito 2 — Página de Dashboard

**User Story:** Como membro da Equipe_TI, quero uma página de Dashboard com indicadores gerenciais e gráficos, para ter uma visão rápida do estado dos chamados.

#### Critérios de Aceitação

1. WHEN a Equipe_TI acessa `/dashboard/`, THE Sistema SHALL renderizar o template `dashboard.html` com os dados dos chamados.
2. THE Sistema SHALL exibir no Dashboard os seguintes KPIs numéricos: total de chamados abertos, chamados em triagem, chamados em atendimento e chamados fechados.
3. THE Sistema SHALL exibir no Dashboard os três gráficos Chart.js atualmente presentes em `relatorios.html`: gráfico de chamados por etiqueta (doughnut), por status (bar) e por atendente (bar horizontal).
4. WHEN o Dashboard é carregado, THE dashboard_js SHALL buscar dados via fetch no endpoint_dashboard (`/relatorios/dashboard/`) e renderizar os gráficos.
5. THE Sistema SHALL proteger a view `dashboard()` com `@login_required`, redirecionando usuários não autenticados para `/login/`.
6. IF a Equipe_TI tenta acessar `/dashboard/` e o usuário autenticado possui `tipo == 'comum'`, THEN THE Sistema SHALL redirecionar para `/meus-chamados/` com mensagem de erro.
7. WHEN a Equipe_TI acessa o Dashboard, THE Sistema SHALL carregar apenas o `dashboard_js` — nenhum outro script de módulo (relatorios_js, agendamento_js) deve ser carregado nessa página.

---

### Requisito 3 — Relatórios Reestruturados

**User Story:** Como membro da Equipe_TI, quero que a página de Relatórios exiba apenas a tabela de consulta e exportação, sem gráficos, para focar na análise de dados tabulares.

#### Critérios de Aceitação

1. THE Sistema SHALL remover de `relatorios.html` todos os elementos HTML dos três gráficos Chart.js (seção "DASHBOARD GRÁFICOS" com os canvas `chartEtiqueta`, `chartStatus`, `chartAtendente`).
2. THE Sistema SHALL manter em `relatorios.html` todos os filtros existentes: Etiqueta, Status, Atendente, Data Inicial, Data Final e Busca textual.
3. THE Sistema SHALL manter em `relatorios.html` a tabela paginada AJAX com os campos: ID, Solicitante, Local, Categoria, Etiqueta, Status, Abertura, Fechamento e Atendente.
4. THE Sistema SHALL manter em `relatorios.html` a funcionalidade de exportação para Excel via modal.
5. WHEN a Equipe_TI acessa `/relatorios/`, THE Sistema SHALL carregar apenas o `relatorios_js` — nenhum outro script de módulo deve ser carregado nessa página.
6. THE endpoint `/relatorios/ajax/` e `/relatorios/exportar/` SHALL permanecer inalterados em comportamento.

---

### Requisito 4 — Model AgendamentoMultimidia

**User Story:** Como desenvolvedor, quero um novo model Django para registrar reservas de multimídia, para que os dados de agendamento sejam persistidos de forma estruturada.

#### Critérios de Aceitação

1. THE Sistema SHALL criar o model `AgendamentoMultimidia` em `chamados/models.py` com os seguintes campos:
   - `solicitante`: ForeignKey para `Usuario`, on_delete=CASCADE
   - `local`: CharField(max_length=200)
   - `data`: DateField
   - `horario_inicio`: TimeField
   - `horario_fim`: TimeField
   - `sala`: CharField(max_length=100)
   - `equipamentos`: JSONField (lista de strings com as escolhas disponíveis)
   - `observacoes`: TextField(blank=True)
   - `status`: CharField com choices `[('Pendente', 'Pendente'), ('Aprovado', 'Aprovado'), ('Recusado', 'Recusado')]`, default `'Pendente'`
   - `created_at`: DateTimeField(auto_now_add=True)
2. THE Sistema SHALL aceitar nos `equipamentos` apenas valores do conjunto: `['Projetor', 'Notebook', 'Caixa de Som', 'Microfone', 'TV', 'Cabo HDMI', 'Outro']`.
3. THE Sistema SHALL gerar uma migration para o model `AgendamentoMultimidia` numerada a partir de `0008`.
4. THE Sistema SHALL registrar `AgendamentoMultimidia` no `admin.py` da app `chamados`.

---

### Requisito 5 — Página de Agendamento de Multimídia

**User Story:** Como membro da Equipe_TI ou Usuario_Comum, quero acessar uma página para solicitar e visualizar agendamentos de equipamentos multimídia, para organizar o uso dos recursos de apresentação.

#### Critérios de Aceitação

1. WHEN qualquer usuário autenticado acessa `/agendamento-multimidia/`, THE Sistema SHALL renderizar o template `agendamento_multimidia.html`.
2. THE Sistema SHALL exibir na página um formulário com os campos: Local, Data, Horário de Início, Horário de Fim, Sala, Equipamentos (checkboxes múltiplos) e Observações.
3. WHEN um usuário autenticado submete o formulário de agendamento com dados válidos, THE Sistema SHALL criar um registro `AgendamentoMultimidia` com `status='Pendente'` e `solicitante` igual ao usuário autenticado.
4. IF o campo `horario_fim` for menor ou igual ao campo `horario_inicio` no formulário submetido, THEN THE Sistema SHALL exibir uma mensagem de erro de validação sem salvar o registro.
5. IF o campo `data` for anterior à data atual no formulário submetido, THEN THE Sistema SHALL exibir uma mensagem de erro de validação sem salvar o registro.
6. IF nenhum equipamento for selecionado no formulário submetido, THEN THE Sistema SHALL exibir uma mensagem de erro de validação sem salvar o registro.
7. THE Sistema SHALL listar abaixo do formulário os agendamentos do usuário autenticado, ordenados por `data` e `horario_inicio` (mais recentes primeiro quando datas iguais).
8. WHILE o usuário autenticado possui `tipo == 'ti'`, THE Sistema SHALL listar todos os agendamentos de todos os usuários na página.
9. THE Sistema SHALL proteger a view com `@login_required`, redirecionando não autenticados para `/login/`.
10. WHEN o agendamento é submetido com dados válidos, THE Sistema SHALL exibir mensagem de sucesso e redirecionar para `/agendamento-multimidia/`.
11. WHEN a página de agendamento é carregada, THE Sistema SHALL carregar apenas o `agendamento_js`.

---

### Requisito 6 — Área do Usuário Comum Atualizada

**User Story:** Como Usuario_Comum, quero ver o botão "Agendar Multimídia" ao lado de "Abrir Chamado", para solicitar reserva de equipamentos diretamente da minha área.

#### Critérios de Aceitação

1. WHEN o Usuario_Comum acessa `/meus-chamados/`, THE Sistema SHALL exibir dois botões de ação: "Abrir Novo Chamado" e "Agendar Multimídia".
2. THE Sistema SHALL posicionar os dois botões no mesmo container, lado a lado, mantendo o layout atual da página `usuario_comum.html`.
3. WHEN o Usuario_Comum clica em "Agendar Multimídia", THE Sistema SHALL navegar para `/agendamento-multimidia/`.
4. THE Sistema SHALL manter o botão "Abrir Novo Chamado" com o comportamento e estilo atuais, sem alterações.

---

### Requisito 7 — Separação de Scripts JavaScript por Módulo

**User Story:** Como desenvolvedor, quero que cada página carregue apenas seu próprio script JavaScript, para evitar conflitos e reduzir o payload desnecessário.

#### Critérios de Aceitação

1. THE Sistema SHALL criar o arquivo `static/chamados/js/dashboard.js` contendo exclusivamente a lógica de inicialização dos gráficos Chart.js e KPIs do Dashboard.
2. THE Sistema SHALL criar o arquivo `static/chamados/js/relatorios.js` contendo exclusivamente a lógica de filtros, busca, paginação AJAX e exportação Excel.
3. THE Sistema SHALL criar o arquivo `static/chamados/js/agendamento.js` contendo exclusivamente as validações do formulário de agendamento: `horario_fim > horario_inicio` e `data >= hoje`.
4. THE Sistema SHALL remover o bloco `<script>` inline de `relatorios.html` após migrar o conteúdo para `relatorios.js`.
5. THE Sistema SHALL manter `kanban.js` exclusivo do Kanban, sem adicionar ou remover lógica deste arquivo.
6. WHEN qualquer template carrega um script de módulo, THE Sistema SHALL usar o template tag `{% static %}` para referenciar o arquivo estático.

---

### Requisito 8 — CSS: Reutilização e Extensão Mínima

**User Story:** Como desenvolvedor, quero reutilizar `kanban.css` para as novas páginas e adicionar apenas classes novas quando necessário, para manter o CSS coeso e sem duplicações.

#### Critérios de Aceitação

1. THE Sistema SHALL referenciar `kanban.css` em todos os novos templates (`dashboard.html`, `agendamento_multimidia.html`) como folha de estilos principal.
2. THE Sistema SHALL adicionar classes CSS novas exclusivamente para elementos que não possuam equivalente em `kanban.css`.
3. THE Sistema SHALL evitar redefinir em blocos `<style>` inline propriedades já declaradas em `kanban.css` (ex: `.sidebar`, `.top-header`, `.main-content`, `.nav-link`).
4. IF novas classes CSS forem necessárias para Dashboard ou Agendamento, THEN THE Sistema SHALL documentá-las com comentários descritivos no bloco `<style>` do respectivo template.

---

### Requisito 9 — Preservação do Sistema Existente

**User Story:** Como administrador do sistema, quero que as funcionalidades existentes (Kanban, Chat, Etiquetas, Autenticação) permaneçam intactas após a reestruturação, para garantir que nenhuma regressão seja introduzida.

#### Critérios de Aceitação

1. THE Sistema SHALL manter o comportamento atual de todas as views existentes: `equipe_ti`, `kanban_polling`, `load_more_chamados`, `detalhe_chamado_ajax`, `etiquetas_chamado`, `salvar_etiquetas_chamado`, `enviar_mensagem`.
2. THE Sistema SHALL manter todas as URLs existentes funcionais sem alteração de padrão de rota.
3. THE Sistema SHALL manter o sistema de autenticação e permissões sem qualquer modificação.
4. THE Sistema SHALL manter o model `Chamado`, `Etiqueta`, `HistoricoEtiqueta`, `MensagemChat` e `Usuario` sem alterações nos campos ou comportamentos existentes.
5. THE Sistema SHALL manter `kanban.js` e `sidebar.js` sem qualquer modificação de conteúdo.
