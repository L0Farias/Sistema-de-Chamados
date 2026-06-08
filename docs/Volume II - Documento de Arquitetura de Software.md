VOLUME II
DOCUMENTO DE ARQUITETURA DE SOFTWARE
SISTEMA DE CHAMADOS TICS
Versão: 1.0 Baseado na Implementação Atual

1. VISÃO ARQUITETURAL
1.1 Objetivo
Este documento descreve a arquitetura do Sistema de Chamados TICS, seus componentes, responsabilidades, interações e decisões arquiteturais.

2. ARQUITETURA GERAL
O sistema adota uma arquitetura monolítica MVC baseada em Django.

Camadas:

Cliente ↓ Templates HTML ↓ Views Django ↓ Models Django ORM ↓ SQLite

3. STACK TECNOLÓGICA
Backend
Framework:

Django 5.2.13

Responsabilidades:

Autenticação
Regras de negócio
Persistência
Controle de permissões
Frontend
Tecnologias:

HTML5
CSS3
Bootstrap 5
Font Awesome
JavaScript Vanilla
Responsabilidades:

Interface
Validações básicas
Interações AJAX
Dashboard Kanban
Persistência
Banco:

SQLite

Responsabilidades:

Armazenamento
Integridade dos dados
Histórico
Comunicação
Protocolo:

HTTP/HTTPS

Padrão:

Request → Response

4. DIAGRAMA C4 - CONTEXTO
Sistema de Chamados TICS

Atores:

Usuário Comum ↓ Sistema ↓ Banco de Dados

Equipe TI ↓ Sistema ↓ Banco de Dados

Administrador ↓ Sistema ↓ Banco de Dados

5. DIAGRAMA C4 - CONTAINERS
Sistema de Chamados TICS

Container 1:

Frontend Web

Tecnologias:

HTML
CSS
Bootstrap
JavaScript
Responsável por:

Interface
Kanban
Formulários
Container 2:

Backend Django

Tecnologias:

Python
Django
Responsável por:

Autenticação
Regras
Permissões
Persistência
Container 3:

Banco de Dados

Tecnologia:

SQLite

Responsável por:

Usuários
Chamados
Mensagens
6. COMPONENTES INTERNOS
Módulo Autenticação
Responsabilidades:

Login
Logout
Recuperação de senha
Controle de sessão
Arquivos:

views.py
forms.py
settings.py
Módulo Chamados
Responsabilidades:

Criar chamados
Consultar chamados
Atualizar status
Arquivos:

models.py
views.py
Módulo Kanban
Responsabilidades:

Visualização operacional
Movimentação de chamados
Arquivos:

kanban.js
dashboard_ti.html
Módulo Chat
Responsabilidades:

Comunicação usuário ↔ técnico
Arquivos:

models.py
views.py
Entidade:

MensagemChat

Módulo Relatórios
Responsabilidades:

Indicadores
Exportações
Arquivos:

views.py
7. MODELO DE DOMÍNIO
Usuario
Representa um usuário autenticado.

Tipos:

comum
ti
Responsabilidades:

Abrir chamados
Atender chamados
Participar do chat
Chamado
Representa uma solicitação técnica.

Responsabilidades:

Armazenar informações
Controlar fluxo operacional
MensagemChat
Representa mensagens associadas a chamados.

Responsabilidades:

Registrar comunicação
Preservar histórico
8. DIAGRAMA DE CLASSES UML
Usuario

Atributos:

username
email
tipo
Relacionamentos:

Usuario 1:N Chamado

Usuario 1:N MensagemChat

Chamado

Atributos:

local
categoria
tipo
problema
status
Relacionamentos:

Chamado 1:N MensagemChat

Chamado N:1 Usuario

MensagemChat

Atributos:

autor
mensagem
data
Relacionamentos:

MensagemChat N:1 Chamado

MensagemChat N:1 Usuario

9. DIAGRAMA ER
USUARIO

PK id

username

email

tipo

↓

CHAMADO

PK id

local

categoria

tipo

problema

status

↓

MENSAGEMCHAT

PK id

mensagem

data

Cardinalidades:

Usuario 1:N Chamado

Usuario 1:N MensagemChat

Chamado 1:N MensagemChat

10. FLUXO DE AUTENTICAÇÃO
Usuário acessa login
Informa credenciais
Django autentica
Sistema identifica perfil
Redirecionamento
Se:

tipo = comum

→ Dashboard Usuário

Se:

tipo = ti

→ Dashboard TI

11. FLUXO OPERACIONAL DE CHAMADOS
Abertura

↓

Novo

↓

Triagem

↓

Em Atendimento

↓

Fechado

Eventos registrados:

Data abertura
Data triagem
Data atendimento
Data fechamento
12. CONTROLE DE ACESSO
Modelo:

RBAC (Role Based Access Control)

Perfis:

Usuário Comum
Técnico TI
Permissões aplicadas:

View-Level Authorization

Implementação:

Validação em Views Django.

13. SEGURANÇA
Autenticação
Implementação:

Django Authentication Framework

Senhas
Armazenamento:

Hash seguro Django

Nunca texto puro.

CSRF
Proteção habilitada.

Sessões
Controle via Session Middleware.

Permissões
Validação por perfil.

14. LOGGING E AUDITORIA
Atualmente:

Auditoria implícita via:

Histórico de chamados
Histórico de mensagens
Datas de transição
Melhoria recomendada:

Tabela AuditLog.

15. ESCALABILIDADE
Estado Atual

SQLite

Monolito

Servidor único

Limitações

Concorrência
Volume de dados
Escalabilidade horizontal
16. ESTRATÉGIA DE EVOLUÇÃO
Fase 1

SQLite → PostgreSQL

Fase 2

Dockerização

Fase 3

Django REST Framework

Fase 4

JWT

Fase 5

Aplicativo Mobile

17. ADRs
ADR-001

Decisão:

Django

Motivo:

Produtividade e segurança.

ADR-002

Decisão:

SQLite

Motivo:

Implantação simplificada.

ADR-003

Decisão:

Bootstrap

Motivo:

Responsividade rápida.

ADR-004

Decisão:

Usuário Customizado

Motivo:

Controle de perfis.

ADR-005

Decisão:

Kanban Operacional

Motivo:

Melhor visualização do fluxo.

18. DÉBITOS TÉCNICOS IDENTIFICADOS
Ausência de API REST
Ausência de testes automatizados
Ausência de logs estruturados
Ausência de cache
Ausência de monitoramento
19. RECOMENDAÇÕES
Curto Prazo

PostgreSQL
Testes Unitários
Docker
Médio Prazo

API REST
JWT
Longo Prazo

Aplicativo Mobile
SLA Automático
IA para classificação
FIM DO VOLUME II