# Core System Requirements

Projeto: Sistema de Chamados TICS

---

RF-001
Título: Autenticação

Descrição:
Usuários devem conseguir autenticar-se utilizando username e senha.

Critérios:
- Login válido cria sessão
- Login inválido retorna erro

---

RF-002
Título: Cadastro de Chamados

Descrição:
Usuários comuns devem conseguir abrir chamados.

Critérios:
- Local obrigatório
- Categoria obrigatória
- Tipo obrigatório
- Problema obrigatório

Resultado:
Status inicial = Novo

---

RF-003
Título: Fluxo Operacional

Descrição:
Chamados devem seguir fluxo controlado.

Estados:

Novo
→ Triagem
→ Em Atendimento
→ Fechado

---

RF-004
Título: Chat

Descrição:
Usuários e técnicos podem trocar mensagens dentro do chamado.

Critérios:
- Mensagem vinculada ao chamado
- Autor registrado
- Histórico preservado

---

RF-005
Título: Controle de Acesso

Descrição:
Perfis possuem permissões distintas.

Perfis:
- comum
- ti