VOLUME IV
ENGENHARIA REVERSA DA IMPLEMENTAÇÃO
Sistema de Chamados TICS

Baseado na Implementação Real do Projeto

Versão: 1.0

1. INVENTÁRIO DO PROJETO
Estrutura Principal
manage.py

requirements.txt

db.sqlite3

sistema_chamados/

chamados/

media/

Aplicação Principal
chamados/

Arquivos identificados:

admin.py
apps.py
forms.py
models.py
urls.py
views.py
Comandos Customizados
chamados/management/commands/

create_TI_user.py
delete_user.py
list_users.py
Objetivo:

Administração de usuários via terminal.

2. MAPEAMENTO COMPLETO DE ROTAS
Página Inicial
URL:

/

View:

index()

Função:

Redireciona para login.

Login
URL:

/login/

View:

login_view()

Template:

login.html

Responsabilidades:

Autenticar usuário
Criar sessão
Redirecionar conforme perfil
Logout
URL:

/logout/

View:

logout_view()

Responsabilidades:

Encerrar sessão
Limpar autenticação
Cadastro Usuário Comum
URL:

/cadastrar-comum/

View:

cadastrar_comum()

Template:

cadastrar_comum.html

Cadastro Técnico
URL:

/cadastrar-ti/

View:

cadastrar_ti()

Template:

cadastrar_ti.html

Permissão:

Somente TI

Dashboard Usuário
URL:

/meus-chamados/

View:

usuario_comum()

Template:

usuario_comum.html

Dashboard TI
URL:

/equipe-ti/

View:

equipe_ti()

Template:

equipe_ti.html

Permissão:

Somente TI

Criar Chamado
URL:

/chamado/novo/

View:

criar_chamado()

Template:

criar_chamado.html

Detalhe Chamado
URL:

/chamado//

View:

detalhe_chamado()

Template:

detalhe_chamado.html

Triagem
URL:

/chamado//triar/

View:

triar_chamado()

Iniciar Atendimento
URL:

/chamado//iniciar/

View:

iniciar_atendimento()

Fechar Chamado
URL:

/chamado//fechar/

View:

fechar_chamado()

Reabrir Chamado
URL:

/chamado//reabrir/

View:

reabrir_chamado()

Chat
URL:

/chamado//mensagem/

View:

enviar_mensagem()

AJAX - Carregamento Incremental
URL:

/load-more-chamados/

View:

load_more_chamados()

Retorno:

JSON

AJAX - Detalhes
URL:

/chamado//ajax/

View:

detalhe_chamado_ajax()

Retorno:

JSON

Relatórios
URL:

/relatorios/

View:

relatorios()

Template:

relatorios.html

Status:

Estrutura criada

Implementação pendente

3. MODELO DE DADOS REAL
Entidade Usuario
Origem:

AbstractUser

Campos Herdados:

username
first_name
last_name
password
email
is_staff
is_active
Campos Customizados:

tipo

Valores:

comum
ti
Restrições:

email UNIQUE

Entidade Chamado
Campos:

id

nome_usuario

local

categoria

tipo

problema

data_abertura

status

atendente

data_triagem

data_atendimento

data_fechamento

Status Existentes
Novo

Triagem

Em Atendimento

Fechado

Tipos Existentes
problema

solicitacao

Entidade MensagemChat
Campos:

id

chamado

autor

mensagem

data

4. RELACIONAMENTOS ORM
Usuario 1:N Chamado

Campo:

nome_usuario

Relacionamento:

Solicitante

Usuario 1:N Chamado

Campo:

atendente

Relacionamento:

Responsável pelo atendimento

Chamado 1:N MensagemChat

Campo:

mensagens

Relacionamento:

Chat interno

Usuario 1:N MensagemChat

Campo:

autor

Relacionamento:

Autor da mensagem

5. DIAGRAMA ER REAL
USUARIO

↓

CHAMADO

↓

MENSAGEMCHAT

Cardinalidades:

USUARIO 1:N CHAMADO

USUARIO 1:N MENSAGEMCHAT

CHAMADO 1:N MENSAGEMCHAT

6. FORMULÁRIOS IMPLEMENTADOS
LoginForm
Campos:

username

password

Objetivo:

Autenticação

UsuarioComumCreationForm
Base:

UserCreationForm

Campos:

username

first_name

last_name

email

password1

password2

Validações:

username único
email único
ChamadoForm
Campos:

local

categoria

tipo

problema

7. REGRAS DE NEGÓCIO EXTRAÍDAS DO CÓDIGO
RN-001

Usuário autenticado é redirecionado automaticamente conforme perfil.

RN-002

Usuário comum não pode acessar dashboard TI.

RN-003

TI não pode acessar dashboard comum.

RN-004

Apenas TI pode cadastrar usuários TI.

RN-005

Chamado criado por usuário comum.

Solicitante:

request.user

RN-006

Status inicial:

Novo

RN-007

Triagem atribui técnico responsável.

RN-008

Início de atendimento atribui técnico responsável.

RN-009

Reabertura remove atendente.

RN-010

Usuário comum só visualiza próprios chamados.

RN-011

Chat registra autor automaticamente.

RN-012

Mensagens vazias não são persistidas.

8. MATRIZ DE AUTORIZAÇÃO REAL
Login

Comum: Sim

TI: Sim

Abrir Chamado

Comum: Sim

TI: Não

Visualizar Próprios Chamados

Comum: Sim

TI: Sim

Visualizar Todos

Comum: Não

TI: Sim

Triagem

Comum: Não

TI: Sim

Atendimento

Comum: Não

TI: Sim

Fechamento

Comum: Não

TI: Sim

Reabertura

Comum: Não

TI: Sim

Cadastro TI

Comum: Não

TI: Sim

Relatórios

Comum: Não

TI: Sim

9. ENDPOINTS AJAX
Load More Chamados
Método:

GET

Parâmetros:

status

page

Retorno:

JSON

Estrutura:

id

nome_usuario

local

categoria

tipo

status

data_abertura

Detalhe Chamado AJAX
Método:

GET

Retorno:

JSON

Campos:

id

problema

nome_usuario

local

categoria

tipo

status

data_abertura

atendente

10. FLUXO REAL DE ESTADOS
Novo

↓

Triagem

↓

Em Atendimento

↓

Fechado

↓

Reabrir

↓

Novo

11. DÉBITOS TÉCNICOS IDENTIFICADOS
DT-001

Datas de triagem, atendimento e fechamento existem no Model, mas não são atualizadas nas Views.

Impacto:

Perda de rastreabilidade temporal.

DT-002

Não existem testes automatizados.

Arquivo:

tests.py vazio.

DT-003

Não existe camada Service.

Lógica concentrada em Views.

DT-004

Ausência de API REST.

DT-005

Ausência de auditoria estruturada.

DT-006

Relatórios ainda não implementados.

12. RISCOS ARQUITETURAIS
Baixo

Crescimento do número de usuários
Médio

Escalabilidade SQLite
Alto

Ausência de testes
Ausência de logs
Ausência de API
13. ESPECIFICAÇÃO OPENAPI FUTURA
POST /login

POST /logout

GET /chamados

POST /chamados

GET /chamados/{id}

PATCH /chamados/{id}

POST /chamados/{id}/triar

POST /chamados/{id}/iniciar

POST /chamados/{id}/fechar

POST /chamados/{id}/reabrir

GET /chamados/{id}/mensagens

POST /chamados/{id}/mensagens

14. PLANO DE MODERNIZAÇÃO
FASE 1

PostgreSQL

FASE 2

Docker

FASE 3

Django REST Framework

FASE 4

JWT

FASE 5

Swagger

FASE 6

Aplicativo Mobile

15. CONCLUSÃO TÉCNICA
O Sistema de Chamados TICS apresenta uma arquitetura monolítica simples, organizada e adequada para o porte atual do projeto.

Pontos Fortes:

Usuário customizado
Controle de perfis
Fluxo operacional completo
Chat integrado
Endpoints AJAX
Organização MVC do Django
Pontos de Evolução:

Testes automatizados
PostgreSQL
API REST
Auditoria
Relatórios completos
Observabilidade
A implementação atual encontra-se apta para evolução incremental sem necessidade de reescrita arquitetural.

FIM DO VOLUME IV