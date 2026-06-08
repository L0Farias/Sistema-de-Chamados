VOLUME III
CASOS DE USO, USER STORIES E BACKLOG SDD
SISTEMA DE CHAMADOS TICS
Versão: 1.0 Baseado na Implementação Atual

1. VISÃO FUNCIONAL
Este documento descreve os fluxos operacionais do sistema sob a perspectiva dos usuários.

Objetivo:

Transformar a implementação existente em especificações rastreáveis para futuras evoluções.

2. ATORES DO SISTEMA
ATOR 01 — USUÁRIO COMUM
Descrição:

Funcionário da instituição que necessita suporte técnico.

Objetivos:

Solicitar atendimento
Acompanhar chamados
Comunicar-se com TI
ATOR 02 — TÉCNICO TI
Descrição:

Profissional responsável pelo atendimento.

Objetivos:

Gerenciar chamados
Atender solicitações
Atualizar status
Registrar interações
ATOR 03 — ADMINISTRADOR
Descrição:

Perfil administrativo da equipe TI.

Objetivos:

Gerenciar usuários
Monitorar indicadores
Administrar sistema
3. USER STORIES
US-001
Como usuário comum

Quero abrir um chamado

Para solicitar suporte técnico.

Critérios de Aceitação:

Local obrigatório
Categoria obrigatória
Tipo obrigatório
Problema obrigatório
Status inicial “Novo”
US-002
Como usuário comum

Quero visualizar meus chamados

Para acompanhar o atendimento.

Critérios:

Exibir apenas chamados próprios
Ordenação cronológica
Exibir status atual
US-003
Como usuário comum

Quero participar do chat

Para fornecer informações adicionais.

Critérios:

Mensagem vinculada ao chamado
Autor registrado
Data registrada
US-004
Como técnico

Quero visualizar todos os chamados

Para gerenciar a fila de atendimento.

Critérios:

Exibição em Kanban
Atualização de status
Filtros operacionais
US-005
Como técnico

Quero iniciar triagem

Para analisar solicitações recebidas.

Critérios:

Apenas chamados “Novo”
Registrar data de triagem
US-006
Como técnico

Quero iniciar atendimento

Para resolver problemas reportados.

Critérios:

Apenas chamados em Triagem
Registrar responsável
US-007
Como técnico

Quero fechar chamados

Para concluir atendimentos.

Critérios:

Registrar data fechamento
Preservar histórico
US-008
Como técnico

Quero reabrir chamados

Para corrigir encerramentos indevidos.

Critérios:

Retornar status para Novo
US-009
Como técnico

Quero cadastrar outros técnicos

Para ampliar a equipe de atendimento.

Critérios:

Apenas perfil TI
E-mail único
Username único
US-010
Como técnico

Quero gerar relatórios

Para acompanhar produtividade.

Critérios:

Indicadores atualizados
Dados consistentes
4. ÉPICOS
EP-001
Gestão de Usuários

Inclui:

Login
Logout
Cadastro
Recuperação de senha
EP-002
Gestão de Chamados

Inclui:

Abertura
Consulta
Atualização
Encerramento
EP-003
Gestão Operacional

Inclui:

Kanban
Triagem
Atendimento
EP-004
Comunicação

Inclui:

Chat interno
EP-005
Relatórios

Inclui:

Dashboard
Indicadores
5. CASOS DE USO
UC-001 — Login
Ator:

Usuário

Pré-condições:

Conta existente

Fluxo Principal:

Informa credenciais
Sistema valida
Cria sessão
Redireciona dashboard
Fluxo Alternativo:

FA-001

Credenciais inválidas

Resultado:

Mensagem de erro

UC-002 — Abrir Chamado
Ator:

Usuário

Fluxo Principal:

Acessa formulário
Preenche dados
Envia
Sistema valida
Sistema salva
Sistema cria chamado
Resultado:

Status = Novo

UC-003 — Visualizar Chamados
Ator:

Usuário

Fluxo Principal:

Acessa dashboard
Sistema consulta chamados
Exibe resultados
UC-004 — Enviar Mensagem
Ator:

Usuário ou Técnico

Fluxo Principal:

Abre chamado
Digita mensagem
Envia
Resultado:

Mensagem registrada

UC-005 — Triagem
Ator:

Técnico

Fluxo Principal:

Seleciona chamado
Inicia triagem
Resultado:

Status = Triagem

UC-006 — Iniciar Atendimento
Ator:

Técnico

Resultado:

Status = Em Atendimento

UC-007 — Fechar Chamado
Ator:

Técnico

Resultado:

Status = Fechado

UC-008 — Reabrir Chamado
Ator:

Técnico

Resultado:

Status = Novo

UC-009 — Cadastrar Técnico
Ator:

Técnico

Fluxo Principal:

Acessa cadastro
Preenche formulário
Sistema valida
Sistema salva
6. MATRIZ DE RASTREABILIDADE
Requisito

User Story

Caso de Uso

RF-001

US-001

UC-002

RF-002

US-002

UC-003

RF-003

US-003

UC-004

RF-004

US-004

UC-005

RF-005

US-005

UC-006

RF-006

US-007

UC-007

7. BPMN OPERACIONAL
Processo:

Abrir Chamado

↓

Novo

↓

Triagem

↓

Em Atendimento

↓

Fechado

Fim

8. CENÁRIOS DE TESTE
CT-001
Objetivo:

Validar abertura.

Passos:

Login
Abrir formulário
Preencher dados
Enviar
Resultado esperado:

Chamado criado.

CT-002
Objetivo:

Validar triagem.

Resultado esperado:

Status atualizado.

CT-003
Objetivo:

Validar fechamento.

Resultado esperado:

Chamado encerrado.

CT-004
Objetivo:

Validar chat.

Resultado esperado:

Mensagem persistida.

9. BACKLOG TÉCNICO
Prioridade Alta

PostgreSQL
Docker
Testes Unitários
Prioridade Média

API REST
JWT
Logs estruturados
Prioridade Baixa

Mobile
SLA automático
Notificações Push
10. PREPARAÇÃO PARA SPEC DRIVEN DEVELOPMENT
Estrutura recomendada:

/specs

/specs/business-rules

/specs/user-stories

/specs/use-cases

/specs/requirements

/specs/architecture

/specs/database

/specs/adrs

/specs/roadmap

Política:

Nenhuma funcionalidade nova poderá ser implementada sem:

Requisito documentado
User Story criada
Caso de Uso definido
Critérios de Aceitação aprovados
FIM DO VOLUME III