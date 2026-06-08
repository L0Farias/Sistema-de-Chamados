VOLUME I
SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
SISTEMA DE CHAMADOS TICS
Versão: 1.0 Data: Junho/2026 Autor: Lucas Farias Status: Produção

CONTROLE DE DOCUMENTO
Campo

Valor

Sistema

Sistema de Chamados TICS

Versão

1.0

Autor

Lucas Farias

Tecnologia Principal

Django 5.2.13

Banco de Dados

SQLite

Metodologia

Spec Driven Development

Status

Em Produção

1. INTRODUÇÃO
1.1 Objetivo
Este documento define integralmente os requisitos funcionais, requisitos não funcionais, regras de negócio e comportamentos esperados do Sistema de Chamados TICS.

O objetivo é servir como referência oficial para:

Desenvolvimento
Evolução
Testes
Auditoria
Onboarding de novos desenvolvedores
1.2 Escopo
O Sistema de Chamados TICS é uma aplicação web destinada ao gerenciamento de solicitações de suporte técnico realizadas por funcionários da Secretaria de Saúde.

O sistema permite:

Registro de chamados
Triagem
Atendimento técnico
Comunicação entre usuários e técnicos
Monitoramento operacional
Relatórios gerenciais
1.3 Definições
Chamado
Solicitação registrada por um usuário para atendimento técnico.

Triagem
Processo de análise inicial do chamado.

Atendimento
Período em que o técnico trabalha na resolução do problema.

Fechamento
Conclusão formal do atendimento.

2. VISÃO GERAL DO PRODUTO
2.1 Problema
Antes da implantação do sistema, as solicitações eram realizadas através de:

WhatsApp
Ligações
Comunicação verbal
E-mail
Consequências:

Falta de rastreabilidade
Perda de solicitações
Ausência de métricas
Baixa visibilidade operacional
2.2 Solução
Centralização de todas as solicitações em plataforma única.

Benefícios:

Histórico completo
Controle operacional
Relatórios
Transparência
Auditoria
3. PERFIS DE USUÁRIO
3.1 Usuário Comum
Representa funcionários que solicitam suporte.

Responsabilidades:

Abrir chamados
Acompanhar chamados
Interagir pelo chat
Restrições:

Não altera status
Não acessa dashboard TI
Não visualiza chamados de terceiros
3.2 Técnico de TI
Representa a equipe responsável pelo atendimento.

Responsabilidades:

Triar chamados
Atender solicitações
Fechar chamados
Utilizar dashboard Kanban
Gerar relatórios
4. REQUISITOS FUNCIONAIS
RF-001 Autenticação
Descrição:

Permitir autenticação de usuários.

Entradas:

Usuário
Senha
Resultado:

Sessão autenticada.

Critérios:

Credenciais válidas
Conta ativa
RF-002 Recuperação de Senha
Descrição:

Permitir redefinição de senha via e-mail.

Pré-condições:

Usuário cadastrado
E-mail válido
Resultado:

Link enviado por SMTP.

RF-003 Cadastro de Chamado
Descrição:

Permitir abertura de chamados.

Campos obrigatórios:

Local
Categoria
Tipo
Problema
Resultado:

Status inicial = Novo

RF-004 Consulta de Chamados
Usuário comum:

Visualiza apenas chamados próprios.

Técnico:

Visualiza todos os chamados.

RF-005 Dashboard Operacional
Disponível apenas para usuários TI.

Permite:

Visualização Kanban
Atualização de status
Monitoramento operacional
RF-006 Chat por Chamado
Permite comunicação vinculada ao chamado.

Funcionalidades:

Enviar mensagem
Visualizar histórico
Registrar autor
RF-007 Triagem
Permite alteração de status:

Novo → Triagem

RF-008 Atendimento
Permite alteração:

Triagem → Em Atendimento

RF-009 Fechamento
Permite alteração:

Em Atendimento → Fechado

RF-010 Reabertura
Permite alteração:

Fechado → Novo

RF-011 Cadastro de Técnicos
Disponível apenas para usuários TI.

Permite:

Criar novo usuário
Definir perfil TI
RF-012 Relatórios
Permite geração de indicadores operacionais.

5. REQUISITOS NÃO FUNCIONAIS
RNF-001 Performance
Tempo médio de resposta:

≤ 2 segundos

RNF-002 Segurança
Implementações identificadas:

Hash de senha Django
CSRF
Controle de sessão
Controle de permissões
RNF-003 Usabilidade
Interface responsiva.

Compatibilidade:

Chrome
Edge
Firefox
RNF-004 Disponibilidade
Meta operacional:

99%

RNF-005 Manutenibilidade
Arquitetura baseada em:

Models
Views
Forms
Templates
6. REGRAS DE NEGÓCIO
RN-001
Usuário comum visualiza apenas seus chamados.

RN-002
Somente usuários TI acessam dashboard operacional.

RN-003
Somente usuários TI alteram status.

RN-004
Todo chamado inicia com status Novo.

RN-005
Todo chamado possui histórico temporal.

Datas registradas:

Abertura
Triagem
Atendimento
Fechamento
RN-006
Somente usuários TI podem cadastrar novos técnicos.

RN-007
E-mail deve ser único.

RN-008
Username deve ser único.

7. FLUXO DE VIDA DO CHAMADO
Estado Inicial:

Novo

Fluxo Principal:

Novo ↓ Triagem ↓ Em Atendimento ↓ Fechado

Fluxo Alternativo:

Fechado ↓ Novo

8. CRITÉRIOS DE ACEITAÇÃO
CA-001

Chamado deve ser criado com sucesso.

CA-002

Usuário comum não acessa dashboard TI.

CA-003

Técnico consegue mover chamados entre colunas.

CA-004

Mensagens ficam vinculadas ao chamado.

CA-005

Histórico permanece armazenado.

9. MATRIZ DE PERMISSÕES
Ação

Usuário

TI

Login

Sim

Sim

Abrir Chamado

Sim

Sim

Ver Próprios Chamados

Sim

Sim

Ver Todos Chamados

Não

Sim

Chat

Sim

Sim

Triagem

Não

Sim

Atendimento

Não

Sim

Fechamento

Não

Sim

Relatórios

Não

Sim

Cadastro TI

Não

Sim

10. INDICADORES OPERACIONAIS
KPIs monitorados:

Chamados Abertos
Chamados Fechados
Chamados em Atendimento
Chamados por Categoria
Produtividade por Técnico
Tempo Médio de Atendimento
11. RESTRIÇÕES TÉCNICAS
Framework:

Django 5.2.13

Banco:

SQLite

Frontend:

Bootstrap 5

Ícones:

Font Awesome

JavaScript:

Vanilla JavaScript

12. CONSIDERAÇÕES FUTURAS
Evoluções previstas:

PostgreSQL
Docker
API REST
JWT
Notificações
SLA Automático
Dashboard Avançado
FIM DO VOLUME I