# Requirements Document

## Introduction

Este documento define os requisitos para a refatoração do sistema de etiquetas dos chamados de TI (TICS), incluindo a migração do campo `etiqueta` de `CharField` para um model `Etiqueta` próprio com suporte a múltiplas etiquetas por chamado, a exibição visual aprimorada com badges coloridos, a reformulação completa do modal do Kanban com layout inspirado em ferramentas profissionais (GitHub/Jira/Linear), e as melhorias de qualidade de código (CSS, JS e backend).

O sistema é uma aplicação Django 5.2 com Bootstrap 5, SQLite, e interface Kanban gerada dinamicamente via JavaScript. O modal é injetado via `innerHTML` pelo `kanban.js`.

---

## Glossary

- **Sistema**: O sistema de chamados TICS (Django 5.2, Bootstrap 5, SQLite).
- **Chamado**: Registro de solicitação de suporte de TI, representado pelo model `Chamado`.
- **Etiqueta**: Categoria visual associada a um chamado, representada pelo novo model `Etiqueta` com campos `nome`, `cor` (hexadecimal) e `ativa`.
- **HistoricoEtiqueta**: Registro de auditoria de adição ou remoção de etiquetas em um chamado.
- **Usuário_TI**: Usuário autenticado com `tipo = 'ti'`.
- **Kanban_JS**: Arquivo `static/chamados/js/kanban.js` responsável pela geração dinâmica do modal e do board Kanban.
- **Modal**: Janela de detalhes de um chamado, gerada pelo `Kanban_JS` via `innerHTML`.
- **Badge**: Elemento visual colorido que representa uma etiqueta, renderizado com a cor hexadecimal do model `Etiqueta`.
- **AJAX_View**: View Django que responde em JSON para requisições assíncronas do `Kanban_JS`.
- **Card_Kanban**: Elemento HTML representando um chamado na coluna do board Kanban, renderizado pelo partial `chamado_card.html`.
- **Dark_Mode**: Modo escuro ativado pela classe `dark-mode` no `body`, controlado pelo `Kanban_JS`.
- **Migration**: Arquivo de migração do Django ORM que altera o schema do banco de dados.
- **Checkbox_Etiqueta**: Elemento `<input type="checkbox">` no modal para seleção de etiquetas.

---

## Requirements

### Requirement 1: Model Etiqueta

**User Story:** Como Usuário_TI, quero que etiquetas sejam gerenciadas como entidades próprias com nome e cor, para que eu possa criar e manter etiquetas reutilizáveis e visualmente distintas.

#### Acceptance Criteria

1. THE Sistema SHALL manter um model `Etiqueta` com os campos `nome` (CharField, máx. 50 caracteres, único), `cor` (CharField, 7 caracteres, formato hexadecimal `#RRGGBB`) e `ativa` (BooleanField, padrão `True`).
2. THE Sistema SHALL registrar o model `Etiqueta` no Django Admin, exibindo as colunas `nome`, `cor` e `ativa` na listagem.
3. THE Sistema SHALL relacionar o model `Chamado` ao model `Etiqueta` via `ManyToManyField` com `blank=True`, substituindo o campo `etiqueta` (CharField).
4. WHEN uma `Migration` é executada, THE Sistema SHALL migrar os dados existentes do campo `etiqueta` (CharField) para registros no model `Etiqueta`, preservando todos os chamados sem perda de dados.
5. IF o campo `nome` de uma `Etiqueta` receber valor com mais de 50 caracteres, THEN THE Sistema SHALL rejeitar o registro com erro de validação.
6. IF o campo `cor` de uma `Etiqueta` não seguir o formato `#RRGGBB`, THEN THE Sistema SHALL rejeitar o registro com erro de validação.

---

### Requirement 2: Múltiplas Etiquetas por Chamado

**User Story:** Como Usuário_TI, quero selecionar múltiplas etiquetas para um chamado via checkboxes no modal, para que eu possa categorizar chamados de forma mais precisa.

#### Acceptance Criteria

1. WHEN o Modal é aberto, THE Kanban_JS SHALL exibir uma lista de Checkbox_Etiqueta com todas as Etiquetas ativas disponíveis.
2. WHEN o Modal é aberto, THE Kanban_JS SHALL marcar como selecionados os Checkbox_Etiqueta correspondentes às etiquetas já associadas ao chamado.
3. WHEN o Usuário_TI altera a seleção de Checkbox_Etiqueta e confirma, THE Sistema SHALL salvar via AJAX_View o conjunto completo de etiquetas selecionadas no chamado, substituindo as associações anteriores.
4. WHEN um Checkbox_Etiqueta é desmarcado e a alteração é confirmada, THE Sistema SHALL remover a associação entre o chamado e a Etiqueta correspondente.
5. THE Sistema SHALL permitir que um chamado seja salvo sem nenhuma etiqueta selecionada (lista vazia).
6. IF o usuário autenticado não for Usuário_TI, THEN THE Sistema SHALL retornar HTTP 403 na AJAX_View de salvamento de etiquetas.

---

### Requirement 3: Histórico de Etiquetas

**User Story:** Como Usuário_TI, quero que toda alteração de etiqueta seja registrada, para que eu possa auditar quem adicionou ou removeu cada etiqueta e quando.

#### Acceptance Criteria

1. THE Sistema SHALL manter um model `HistoricoEtiqueta` com os campos: `chamado` (ForeignKey para `Chamado`), `etiqueta` (ForeignKey para `Etiqueta`), `acao` (CharField com choices `'adicionada'` e `'removida'`), `usuario` (ForeignKey para `Usuario`), e `data` (DateTimeField, automático).
2. WHEN uma etiqueta é adicionada a um chamado via AJAX_View, THE Sistema SHALL criar um registro `HistoricoEtiqueta` com `acao = 'adicionada'`.
3. WHEN uma etiqueta é removida de um chamado via AJAX_View, THE Sistema SHALL criar um registro `HistoricoEtiqueta` com `acao = 'removida'`.
4. WHEN o Modal é aberto, THE Kanban_JS SHALL exibir os registros de `HistoricoEtiqueta` do chamado na seção de histórico, incluindo o nome da etiqueta, a ação, o usuário e a data.
5. THE Sistema SHALL registrar o model `HistoricoEtiqueta` no Django Admin.

---

### Requirement 4: AJAX Views para Etiquetas

**User Story:** Como Usuário_TI, quero que as operações de etiqueta ocorram sem recarregar a página, para que a experiência no Kanban seja fluida.

#### Acceptance Criteria

1. THE Sistema SHALL expor uma AJAX_View em `GET /chamado/<pk>/etiquetas/` que retorna JSON com a lista de todas as Etiquetas ativas (`id`, `nome`, `cor`) e os `ids` das etiquetas já associadas ao chamado.
2. THE Sistema SHALL expor uma AJAX_View em `POST /chamado/<pk>/etiquetas/salvar/` que recebe uma lista de `ids` de etiquetas e atualiza o ManyToManyField do chamado, gerando registros de `HistoricoEtiqueta`.
3. WHEN a AJAX_View de detalhes (`/chamado/<pk>/ajax/`) é chamada, THE Sistema SHALL incluir no JSON de resposta a lista de etiquetas do chamado com `id`, `nome` e `cor` de cada uma.
4. IF o usuário não estiver autenticado em qualquer AJAX_View de etiquetas, THEN THE Sistema SHALL retornar HTTP 403.
5. IF o usuário autenticado não for Usuário_TI na AJAX_View de salvamento, THEN THE Sistema SHALL retornar HTTP 403.

---

### Requirement 5: Exibição de Badges no Modal

**User Story:** Como Usuário_TI, quero ver badges coloridos das etiquetas no cabeçalho do modal, para que eu identifique visualmente a categorização do chamado.

#### Acceptance Criteria

1. WHEN o Modal é aberto e o chamado possui etiquetas associadas, THE Kanban_JS SHALL renderizar um Badge por etiqueta no cabeçalho do modal, usando a cor hexadecimal do campo `cor` da `Etiqueta` como `background-color` inline.
2. WHEN o Modal é aberto e o chamado não possui etiquetas associadas, THE Kanban_JS SHALL exibir o texto "Sem etiqueta" no lugar dos badges.
3. WHEN as etiquetas são salvas com sucesso via AJAX, THE Kanban_JS SHALL atualizar os badges no cabeçalho do modal sem recarregar a página.
4. THE Kanban_JS SHALL garantir que o texto dos badges tenha contraste legível em relação à cor de fundo (`color: #fff` ou `color: #000` conforme luminância da cor hexadecimal).

---

### Requirement 6: Exibição de Etiquetas no Card do Kanban

**User Story:** Como Usuário_TI, quero ver as etiquetas diretamente no card do Kanban, para que eu tenha visibilidade da categorização sem abrir o modal.

#### Acceptance Criteria

1. WHEN o board Kanban é renderizado, THE Sistema SHALL exibir no Card_Kanban os badges das etiquetas do chamado, usando a cor hexadecimal como `background-color` inline.
2. IF o chamado não possuir etiquetas associadas, THEN THE Sistema SHALL omitir a seção de etiquetas no Card_Kanban, sem exibir espaço vazio.
3. THE Sistema SHALL atualizar o template `chamado_card.html` para iterar sobre `chamado.etiquetas.all` e renderizar os badges.

---

### Requirement 7: Layout do Modal

**User Story:** Como Usuário_TI, quero que o modal tenha um layout profissional inspirado em GitHub/Jira/Linear, para que a visualização e o gerenciamento de chamados sejam mais eficientes.

#### Acceptance Criteria

1. THE Kanban_JS SHALL gerar o Modal com uma coluna principal (larga) contendo as seções "Informações", "Descrição do Problema" e "Histórico", e uma coluna lateral contendo as seções "Etiquetas" e "Ações".
2. THE Kanban_JS SHALL renderizar a seção "Informações" com layout de pares chave–valor alinhados, onde o rótulo e o valor são separados por alinhamento pontilhado (ex.: `Solicitante ........... Fulano`).
3. THE Kanban_JS SHALL renderizar cada evento do histórico do chamado como um card individual com borda lateral colorida, contendo evento, responsável e data/hora.
4. THE Kanban_JS SHALL aplicar a classe `chamado-modal` ao `modal-content` e a classe `chamado-header` ao `modal-header`, mantendo a compatibilidade com os seletores CSS existentes.
5. WHILE o Dark_Mode estiver ativo, THE Kanban_JS SHALL garantir que o Modal use as cores definidas nos seletores `body.dark-mode .chamado-modal` e `body.dark-mode .card` do `kanban.css`.
6. THE Sistema SHALL garantir que o Modal seja responsivo para desktop (≥1200px), notebook (≥992px), tablet (≥768px) e mobile (<768px), usando o grid Bootstrap 5.

---

### Requirement 8: Correções de CSS

**User Story:** Como desenvolvedor, quero que o CSS do kanban seja limpo e consistente com o HTML gerado pelo JS, para que os estilos sejam aplicados corretamente.

#### Acceptance Criteria

1. THE Sistema SHALL remover a regra `body { border: 10px solid red !important; }` do arquivo `kanban.css`.
2. THE Sistema SHALL garantir que todos os seletores CSS em `kanban.css` correspondam às classes HTML geradas pelo `Kanban_JS` (ex.: `.chamado-modal`, `.chamado-header`, `.chamado-card`).
3. THE Sistema SHALL garantir que o `Kanban_JS` aplique as classes `.chamado-modal` e `.chamado-header` nos elementos corretos do Modal ao gerar o HTML via `innerHTML`.
4. THE Sistema SHALL adicionar estilos CSS para os Badges de etiquetas, incluindo variantes para Dark_Mode.
5. THE Sistema SHALL adicionar estilos CSS para o alinhamento pontilhado da seção de Informações do Modal.

---

### Requirement 9: Qualidade e Compatibilidade

**User Story:** Como desenvolvedor, quero que o código gerado seja modular, sem duplicação e compatível com Bootstrap 5 e o Dark Mode existente, para que a manutenção futura seja simples.

#### Acceptance Criteria

1. THE Kanban_JS SHALL encapsular a lógica de renderização do Modal em funções nomeadas reutilizáveis, sem duplicação de HTML entre chamadas.
2. THE Sistema SHALL garantir que nenhum erro seja exibido no console do navegador durante a abertura do modal, salvamento de etiquetas e transições de status.
3. THE Sistema SHALL garantir que as migrations geradas sejam reversíveis e incluam a migração de dados do campo antigo `etiqueta` (CharField) para o novo model `Etiqueta`.
4. THE Sistema SHALL garantir que a view `relatorios_ajax` e a view `relatorios_dashboard` continuem funcionando corretamente após a migração do campo `etiqueta` para ManyToManyField, adaptando os filtros de etiqueta.
5. WHEN o Modal é aberto em dispositivo mobile (<768px), THE Kanban_JS SHALL exibir a coluna lateral abaixo da coluna principal em layout de coluna única.
