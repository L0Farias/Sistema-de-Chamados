# Sprint 0 — Estabilização do Sistema de Chamados TICS

**Status:** Planned
**Prioridade:** Crítica
**Origem:** Relatório de Engenharia de Software — 01/06/2026
**Escopo:** Correção de todos os itens classificados como Crítico e Alto no relatório de análise

---

## Contexto

A análise de engenharia identificou 5 itens críticos e 14 itens de alta prioridade no sistema atual.
Antes de qualquer evolução (API REST, PostgreSQL, Docker), o sistema precisa ser estabilizado.
Esta sprint não adiciona funcionalidades — apenas corrige o que está quebrado ou inseguro.

---

## Requisitos

### RF-S0-001 — Exibição correta dos chamados do usuário comum

**Prioridade:** Crítico
**Origem:** BUG-001

A view `usuario_comum` deve consultar e passar ao template a lista de chamados
pertencentes ao usuário autenticado, ordenados por data de abertura decrescente.

Critérios:
- A variável `meus_chamados` deve ser passada ao contexto do template
- Apenas chamados do próprio usuário devem ser exibidos
- Quando não houver chamados, o estado vazio deve ser exibido corretamente
- A tabela deve renderizar todos os campos: ID, data, local, categoria, tipo, status

---

### RF-S0-002 — Badge de status com classes CSS válidas

**Prioridade:** Alto
**Origem:** BUG-002

O badge de status em `usuario_comum.html` deve aplicar classes Bootstrap válidas
de acordo com o valor do status do chamado.

Critérios:
- `Novo` → `bg-primary`
- `Triagem` → `bg-warning text-dark`
- `Em Atendimento` → `bg-info text-dark`
- `Fechado` → `bg-success`
- Nenhum status deve resultar em badge sem cor

---

### RF-S0-003 — Botões de ação rápida no modal Kanban funcionais

**Prioridade:** Alto
**Origem:** BUG-003

Os botões Triar, Iniciar Atendimento, Fechar Chamado e Reabrir no modal do Kanban
devem executar as respectivas ações via requisição POST autenticada.

Critérios:
- Cada botão deve submeter um formulário POST para a URL de ação correspondente
- O CSRF token deve estar presente em cada formulário
- Após a ação, o Kanban deve refletir o novo estado do chamado
- Botões devem ser exibidos condicionalmente conforme o status atual do chamado

---

### RF-S0-004 — Ações de transição de estado protegidas por POST

**Prioridade:** Crítico
**Origem:** SEC-001, DJANGO-006

As views `triar_chamado`, `iniciar_atendimento`, `fechar_chamado` e `reabrir_chamado`
devem aceitar exclusivamente requisições POST.

Critérios:
- Requisições GET devem retornar HTTP 405 Method Not Allowed
- O decorator `@require_POST` deve ser aplicado em todas as quatro views
- A proteção CSRF deve estar ativa em todos os formulários que disparam essas ações

---

### RF-S0-005 — Separação de configurações por ambiente

**Prioridade:** Crítico
**Origem:** DJANGO-001, SEC-002, REFAC-004

O projeto deve possuir arquivos de configuração distintos para desenvolvimento e produção.

Critérios:
- `settings/base.py` contém configurações comuns
- `settings/dev.py` herda de base, define `DEBUG=True` e `ALLOWED_HOSTS=['localhost', '127.0.0.1']`
- `settings/prod.py` herda de base, define `DEBUG=False` e `ALLOWED_HOSTS` via variável de ambiente
- `SECRET_KEY` não deve ter fallback hardcoded — deve lançar erro se ausente
- O comando `manage.py` deve apontar para `settings.dev` por padrão no desenvolvimento

---

### RF-S0-006 — Validação de variáveis de ambiente obrigatórias

**Prioridade:** Alto
**Origem:** SEC-003, DJANGO-002

O sistema deve validar na inicialização a presença das variáveis de ambiente críticas.

Critérios:
- `SECRET_KEY` ausente deve impedir a inicialização com mensagem clara
- `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` ausentes devem gerar aviso no log em dev
- `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` ausentes devem impedir inicialização em prod
- `DEFAULT_FROM_EMAIL` nunca deve ser `None`

---

### RF-S0-007 — Preenchimento dos timestamps de transição de estado

**Prioridade:** Alto
**Origem:** BUG-005, DEAD-004

As views de transição de estado devem registrar o timestamp correspondente
no momento em que a transição ocorre.

Critérios:
- `triar_chamado` deve preencher `data_triagem = timezone.now()`
- `iniciar_atendimento` deve preencher `data_atendimento = timezone.now()`
- `fechar_chamado` deve preencher `data_fechamento = timezone.now()`
- `reabrir_chamado` deve limpar `data_triagem`, `data_atendimento` e `data_fechamento`

---

### RF-S0-008 — Registro dos models no Django Admin

**Prioridade:** Alto
**Origem:** BUG-007, DJANGO-004

Os models `Usuario`, `Chamado` e `MensagemChat` devem estar registrados e configurados
no painel administrativo do Django.

Critérios:
- `Usuario` exibe: username, email, tipo, is_active, date_joined
- `Chamado` exibe: id, nome_usuario, status, categoria, local, data_abertura, atendente
- `Chamado` permite filtro por status e busca por nome_usuario e categoria
- `MensagemChat` exibe: chamado, autor, data

---

### RF-S0-009 — Correção do texto da tela de recuperação de senha

**Prioridade:** Médio
**Origem:** BUG-006

O texto instrucional em `password_reset.html` deve descrever corretamente
o campo solicitado pelo formulário Django.

Critérios:
- O texto deve indicar que o usuário deve digitar seu **e-mail cadastrado**
- O fluxo de recuperação deve funcionar corretamente com o campo email

---

### RF-S0-010 — Resolução do problema N+1 nas queries do Kanban

**Prioridade:** Alto
**Origem:** PERF-001, DJANGO-003

A query principal da view `equipe_ti` deve usar `select_related` para evitar
queries adicionais por chamado ao acessar ForeignKeys no template.

Critérios:
- `select_related('nome_usuario', 'atendente')` aplicado na query principal
- O número de queries por carregamento do Kanban não deve crescer com o volume de chamados
- Verificável via Django Debug Toolbar

---

### RF-S0-011 — Botão de colapsar sidebar funcional

**Prioridade:** Alto
**Origem:** DEAD-001

O elemento HTML com `id="sidebarToggle"` deve existir no template `equipe_ti.html`
para que o JavaScript em `sidebar.js` possa funcionar.

Critérios:
- Botão visível na interface do Kanban
- Clicar no botão colapsa/expande a sidebar
- O estado é persistido no `localStorage`
- A transição CSS ocorre suavemente

---

## Design Técnico

### Estrutura de arquivos afetados

```
sistema_chamados/
  settings/
    __init__.py       ← novo
    base.py           ← novo (extraído de settings.py)
    dev.py            ← novo
    prod.py           ← novo
  settings.py         ← removido após migração

chamados/
  admin.py            ← implementar registros
  views.py            ← corrigir BUG-001, BUG-005, SEC-001, PERF-001
  
templates/chamados/
  usuario_comum.html  ← corrigir BUG-002
  equipe_ti.html      ← adicionar sidebarToggle (DEAD-001)
  password_reset.html ← corrigir BUG-006

static/chamados/js/
  kanban.js           ← implementar ações dos botões do modal (BUG-003)
```

---

### Design: Separação de settings (RF-S0-005 e RF-S0-006)

```
base.py
  - INSTALLED_APPS, MIDDLEWARE, TEMPLATES
  - AUTH_USER_MODEL, CRISPY, LOGIN_URL
  - STATIC, MEDIA
  - SECRET_KEY = os.environ['SECRET_KEY']  ← sem fallback, KeyError se ausente

dev.py
  - from .base import *
  - DEBUG = True
  - ALLOWED_HOSTS = ['localhost', '127.0.0.1']
  - DATABASES = SQLite
  - EMAIL_BACKEND = console (sem SMTP real)

prod.py
  - from .base import *
  - DEBUG = False
  - ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')
  - DATABASES = PostgreSQL (preparado para futura migração)
  - EMAIL_BACKEND = SMTP com validação de presença das variáveis
```

`manage.py` e `wsgi.py` apontam para `sistema_chamados.settings.dev` por padrão.
Em produção, a variável `DJANGO_SETTINGS_MODULE` é definida explicitamente.

---

### Design: Ações POST no modal Kanban (RF-S0-003 e RF-S0-004)

O modal em `kanban.js` deve gerar formulários POST dinâmicos para cada ação,
usando o `chamadoId` carregado via AJAX. Os botões devem ser condicionais ao status:

```
status Novo       → exibe: [Triar]
status Triagem    → exibe: [Iniciar Atendimento] [Reabrir]
status Em Atend.  → exibe: [Fechar Chamado] [Reabrir]
status Fechado    → exibe: [Reabrir]
```

O CSRF token deve ser lido do cookie `csrftoken` e incluído no formulário gerado.
Após submit bem-sucedido, o modal fecha e a página recarrega para refletir o novo estado.

---

### Design: Decorator de permissão TI (ARCH-002 — preparação)

Nesta sprint, as 4 views de ação recebem `@require_POST` como correção imediata.
A extração para decorator customizado `@ti_required` é preparada como refatoração
mas não é obrigatória para o aceite desta sprint — fica registrada como débito técnico
a ser endereçado na Sprint 1.

---

### Design: Admin (RF-S0-008)

```python
# admin.py — estrutura conceitual

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'tipo', 'is_active', 'date_joined']
    list_filter = ['tipo', 'is_active']

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome_usuario', 'status', 'categoria', 'local', 'data_abertura', 'atendente']
    list_filter = ['status', 'tipo']
    search_fields = ['nome_usuario__username', 'categoria', 'local']

@admin.register(MensagemChat)
class MensagemChatAdmin(admin.ModelAdmin):
    list_display = ['chamado', 'autor', 'data']
    list_filter = ['chamado__status']
```

---

## Tasks

### TASK-S0-01 — Corrigir view `usuario_comum` (BUG-001)
**Arquivo:** `chamados/views.py`
**Estimativa:** 30 min

- Adicionar query `meus_chamados = Chamado.objects.filter(nome_usuario=request.user).order_by('-data_abertura')`
- Passar `meus_chamados` no contexto do `render()`
- Verificar que o template recebe e exibe a variável corretamente

---

### TASK-S0-02 — Corrigir badge de status (BUG-002)
**Arquivo:** `templates/chamados/usuario_comum.html`
**Estimativa:** 20 min

- Substituir `bg-{{ chamado.status|lower|slice:1 }}` por lógica condicional explícita
- Mapear cada status para sua classe Bootstrap correspondente
- Testar visualmente todos os 4 status

---

### TASK-S0-03 — Proteger ações de estado com `@require_POST` (SEC-001, DJANGO-006)
**Arquivo:** `chamados/views.py`
**Estimativa:** 30 min

- Importar `from django.views.decorators.http import require_POST`
- Aplicar `@require_POST` em: `triar_chamado`, `iniciar_atendimento`, `fechar_chamado`, `reabrir_chamado`
- Verificar que requisições GET retornam 405

---

### TASK-S0-04 — Implementar botões de ação no modal Kanban (BUG-003)
**Arquivo:** `static/chamados/js/kanban.js`
**Estimativa:** 2h

- Ler o CSRF token do cookie no JS
- Gerar formulários POST dinâmicos para cada ação com base no `chamadoId`
- Implementar lógica condicional de exibição dos botões por status
- Testar cada ação a partir do modal

---

### TASK-S0-05 — Preencher timestamps de transição (BUG-005, DEAD-004)
**Arquivo:** `chamados/views.py`
**Estimativa:** 30 min

- `triar_chamado`: adicionar `chamado.data_triagem = timezone.now()`
- `iniciar_atendimento`: adicionar `chamado.data_atendimento = timezone.now()`
- `fechar_chamado`: adicionar `chamado.data_fechamento = timezone.now()`
- `reabrir_chamado`: limpar os três campos com `None`

---

### TASK-S0-06 — Separar settings por ambiente (DJANGO-001, SEC-002, REFAC-004)
**Arquivos:** `sistema_chamados/settings/`
**Estimativa:** 1h

- Criar diretório `sistema_chamados/settings/` com `__init__.py`
- Criar `base.py` com configurações comuns extraídas de `settings.py`
- Criar `dev.py` com `DEBUG=True`, SQLite, email console
- Criar `prod.py` com `DEBUG=False`, validações de env vars
- Remover fallback hardcoded da `SECRET_KEY`
- Atualizar `manage.py`, `wsgi.py` e `asgi.py`
- Atualizar `.env.example` com todas as variáveis necessárias

---

### TASK-S0-07 — Validar variáveis de ambiente obrigatórias (SEC-003, DJANGO-002)
**Arquivo:** `sistema_chamados/settings/base.py` e `prod.py`
**Estimativa:** 30 min

- `SECRET_KEY`: usar `os.environ['SECRET_KEY']` sem fallback
- Em `prod.py`: validar presença de `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL` deve usar o valor de `EMAIL_HOST_USER` com fallback seguro
- Criar `.env.example` documentando todas as variáveis

---

### TASK-S0-08 — Implementar admin.py (BUG-007, DJANGO-004)
**Arquivo:** `chamados/admin.py`
**Estimativa:** 45 min

- Registrar `Usuario` com `UserAdmin` customizado
- Registrar `Chamado` com `list_display`, `list_filter` e `search_fields`
- Registrar `MensagemChat` com `list_display`
- Verificar funcionamento no painel `/admin/`

---

### TASK-S0-09 — Corrigir texto de recuperação de senha (BUG-006)
**Arquivo:** `templates/chamados/password_reset.html`
**Estimativa:** 10 min

- Substituir "Digite seu nome de usuário" por "Digite seu e-mail cadastrado"
- Verificar que o fluxo completo de recuperação funciona end-to-end

---

### TASK-S0-10 — Resolver N+1 no Kanban (PERF-001, DJANGO-003)
**Arquivo:** `chamados/views.py`
**Estimativa:** 20 min

- Adicionar `select_related('nome_usuario', 'atendente')` na query de `equipe_ti`
- Verificar redução de queries com Django Debug Toolbar

---

### TASK-S0-11 — Adicionar botão sidebarToggle ao template (DEAD-001)
**Arquivo:** `templates/chamados/equipe_ti.html`
**Estimativa:** 30 min

- Adicionar elemento `<button id="sidebarToggle">` visível na interface
- Verificar que `sidebar.js` detecta o elemento e aplica o comportamento
- Testar colapso/expansão e persistência no `localStorage`

---

### TASK-S0-12 — Remover imports duplicados de `JsonResponse` (DEAD-005)
**Arquivo:** `chamados/views.py`
**Estimativa:** 5 min

- Manter apenas o import no topo do arquivo
- Remover o import duplicado na seção AJAX

---

## Critérios de Aceite da Sprint

### CA-01 — Usuário comum vê seus chamados
- [ ] Acessar `/meus-chamados/` com usuário que possui chamados exibe a tabela preenchida
- [ ] Acessar com usuário sem chamados exibe o estado vazio correto
- [ ] Chamados de outros usuários não aparecem na listagem

### CA-02 — Badges de status visualmente corretos
- [ ] Chamado com status `Novo` exibe badge azul (`bg-primary`)
- [ ] Chamado com status `Triagem` exibe badge amarelo (`bg-warning`)
- [ ] Chamado com status `Em Atendimento` exibe badge ciano (`bg-info`)
- [ ] Chamado com status `Fechado` exibe badge verde (`bg-success`)

### CA-03 — Ações do modal Kanban funcionam
- [ ] Clicar em "Triar" em chamado `Novo` muda status para `Triagem`
- [ ] Clicar em "Iniciar Atendimento" em chamado `Triagem` muda para `Em Atendimento`
- [ ] Clicar em "Fechar Chamado" muda status para `Fechado`
- [ ] Clicar em "Reabrir" muda status para `Novo`
- [ ] Botões corretos são exibidos para cada status

### CA-04 — Ações de estado rejeitam GET
- [ ] `GET /chamado/1/triar/` retorna HTTP 405
- [ ] `GET /chamado/1/fechar/` retorna HTTP 405
- [ ] `GET /chamado/1/iniciar/` retorna HTTP 405
- [ ] `GET /chamado/1/reabrir/` retorna HTTP 405

### CA-05 — Timestamps preenchidos
- [ ] Após triar: `chamado.data_triagem` não é `None`
- [ ] Após iniciar atendimento: `chamado.data_atendimento` não é `None`
- [ ] Após fechar: `chamado.data_fechamento` não é `None`
- [ ] Após reabrir: os três campos voltam a `None`

### CA-06 — Settings por ambiente
- [ ] `python manage.py runserver` usa `settings.dev` por padrão
- [ ] `DEBUG=True` não está presente em `settings/prod.py`
- [ ] Iniciar sem `SECRET_KEY` no ambiente lança `KeyError` com mensagem clara
- [ ] `ALLOWED_HOSTS` em dev não inclui `'*'`

### CA-07 — Admin funcional
- [ ] `/admin/chamados/chamado/` lista chamados com filtros funcionando
- [ ] `/admin/chamados/usuario/` lista usuários com filtro por tipo
- [ ] Busca por categoria em chamados retorna resultados corretos

### CA-08 — Texto de recuperação de senha correto
- [ ] A tela `/password_reset/` instrui o usuário a digitar o e-mail
- [ ] O fluxo completo de recuperação funciona (envio de email em dev via console)

### CA-09 — N+1 resolvido
- [ ] Django Debug Toolbar mostra número fixo de queries no Kanban independente do volume
- [ ] Número de queries não aumenta ao adicionar mais chamados

### CA-10 — Sidebar toggle funcional
- [ ] Botão de colapsar sidebar está visível no Kanban
- [ ] Clicar no botão colapsa a sidebar
- [ ] Recarregar a página mantém o estado colapsado/expandido

---

## Plano de Testes

### Testes Manuais — Fluxo Crítico

**Cenário 1: Usuário comum visualiza chamados**
1. Criar usuário comum via `/cadastrar-comum/`
2. Criar 3 chamados com status diferentes
3. Acessar `/meus-chamados/`
4. Verificar que os 3 chamados aparecem na tabela
5. Verificar que badges têm cores corretas para cada status

**Cenário 2: Técnico TI executa ações via modal**
1. Fazer login como usuário TI
2. Acessar `/equipe-ti/`
3. Clicar em um card de chamado `Novo`
4. Verificar que apenas o botão "Triar" aparece
5. Clicar em "Triar" e verificar que o chamado move para coluna Triagem
6. Repetir para cada transição de estado

**Cenário 3: Proteção de ações via GET**
1. Fazer login como usuário TI
2. Acessar diretamente `http://localhost:8000/chamado/1/fechar/` via browser
3. Verificar resposta HTTP 405

**Cenário 4: Settings sem SECRET_KEY**
1. Remover `SECRET_KEY` do `.env`
2. Executar `python manage.py runserver`
3. Verificar que o servidor não sobe e exibe erro claro

**Cenário 5: Admin**
1. Acessar `/admin/` com superusuário
2. Verificar presença de `Chamados`, `Usuários`, `Mensagens`
3. Testar filtro por status em Chamados
4. Testar busca por categoria

---

### Testes Automatizados — Escopo Mínimo desta Sprint

Os testes automatizados desta sprint cobrem apenas os bugs corrigidos.
A suite completa é escopo da feature `test-suite.md`.

**`tests.py` — casos a implementar:**

```
TestUsuarioComumView
  test_lista_apenas_chamados_do_usuario
  test_nao_lista_chamados_de_outros_usuarios
  test_contexto_contem_meus_chamados

TestAcoesTI
  test_triar_via_post_retorna_redirect
  test_triar_via_get_retorna_405
  test_fechar_via_get_retorna_405
  test_iniciar_via_get_retorna_405
  test_reabrir_via_get_retorna_405

TestTimestamps
  test_data_triagem_preenchida_ao_triar
  test_data_atendimento_preenchida_ao_iniciar
  test_data_fechamento_preenchida_ao_fechar
  test_timestamps_limpos_ao_reabrir

TestSettings
  test_secret_key_ausente_lanca_erro
```

---

## Dependências e Riscos

**Dependências:**
- Nenhuma dependência externa nova é introduzida nesta sprint
- Todos os pacotes já estão em `requirements.txt`

**Riscos:**

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Migração de settings quebra deploy existente | Média | Alto | Testar `manage.py check` antes de finalizar |
| Botões POST no modal exigem reload de página | Baixa | Médio | Aceito nesta sprint; AJAX completo é Sprint 1 |
| `@require_POST` quebra testes existentes que usam GET | Baixa | Baixo | Não há testes automatizados atualmente |

---

## Definição de Pronto (DoD)

- [ ] Todos os 12 critérios de aceite verificados manualmente
- [ ] Testes automatizados listados implementados e passando
- [ ] `python manage.py check` sem erros
- [ ] `python manage.py check --deploy` sem warnings críticos em `prod.py`
- [ ] Nenhum `print()` ou `console.log()` de debug deixado no código
- [ ] `.env.example` atualizado com todas as variáveis necessárias
- [ ] `README.md` atualizado com instruções de configuração do ambiente
