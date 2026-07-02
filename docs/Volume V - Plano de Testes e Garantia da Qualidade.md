VOLUME V
PLANO DE TESTES E GARANTIA DA QUALIDADE
SISTEMA DE CHAMADOS TICS
Versão: 1.0 Baseado na Implementação Atual

1. OBJETIVO
Este documento estabelece a estratégia oficial de testes do Sistema de Chamados TICS.

Seu objetivo é garantir:

Confiabilidade
Estabilidade
Segurança
Rastreabilidade
Evolução segura
2. ESCOPO DOS TESTES
Serão testados:

✓ Autenticação

✓ Cadastro de usuários

✓ Abertura de chamados

✓ Fluxo operacional

✓ Chat

✓ Controle de permissões

✓ Dashboard

✓ AJAX

✓ Relatórios

✓ Banco de dados

3. ESTRATÉGIA DE QUALIDADE
A qualidade será garantida através de:

Camada 1

Testes Unitários

↓

Camada 2

Testes de Integração

↓

Camada 3

Testes Funcionais

↓

Camada 4

Testes de Aceitação

↓

Camada 5

Testes de Regressão

4. TESTES UNITÁRIOS
Objetivo:

Validar componentes isoladamente.

Ferramenta:

Django Test Framework

TU-001
Entidade Usuario

Validar:

criação
email único
username único
tipo correto
Resultado esperado:

Objeto persistido corretamente.

TU-002
Entidade Chamado

Validar:

status inicial
tipo
categoria
relacionamentos
Resultado esperado:

Chamado criado.

TU-003
Entidade MensagemChat

Validar:

vínculo com chamado
vínculo com autor
data automática
Resultado esperado:

Mensagem registrada.

TU-004
LoginForm

Validar:

credenciais válidas
credenciais inválidas
Resultado esperado:

Comportamento correto.

TU-005
ChamadoForm

Validar:

campos obrigatórios
validações
Resultado esperado:

Formulário consistente.

5. TESTES DE INTEGRAÇÃO
Objetivo:

Validar interação entre módulos.

TI-001
Usuário → Chamado

Fluxo:

Criar usuário

↓

Abrir chamado

Resultado esperado:

Chamado vinculado corretamente.

TI-002
Chamado → Chat

Fluxo:

Criar chamado

↓

Enviar mensagem

Resultado esperado:

Mensagem vinculada.

TI-003
Chamado → Fluxo de Estados

Novo

↓

Triagem

↓

Em Atendimento

↓

Fechado

Resultado esperado:

Estados atualizados corretamente.

6. TESTES FUNCIONAIS
Objetivo:

Validar funcionalidades completas.

TF-001
Login

Passos:

Acessar login
Inserir usuário válido
Entrar
Resultado:

Dashboard correto.

TF-002
Abertura de Chamado

Passos:

Login
Criar chamado
Salvar
Resultado:

Status Novo.

TF-003
Triagem

Passos:

Login TI
Abrir dashboard
Triar chamado
Resultado:

Status Triagem.

TF-004
Atendimento

Passos:

Selecionar chamado
Iniciar atendimento
Resultado:

Status Em Atendimento.

TF-005
Fechamento

Passos:

Abrir chamado
Fechar
Resultado:

Status Fechado.

TF-006
Reabertura

Passos:

Selecionar chamado fechado
Reabrir
Resultado:

Status Novo.

TF-007
Chat

Passos:

Abrir chamado
Enviar mensagem
Resultado:

Mensagem exibida.

7. TESTES DE SEGURANÇA
Objetivo:

Garantir proteção dos dados.

TS-001
Acesso sem autenticação

Resultado esperado:

Redirecionar login.

TS-002
Usuário comum acessando dashboard TI

Resultado esperado:

Negar acesso.

TS-003
Usuário comum tentando alterar status

Resultado esperado:

Negar operação.

TS-004
Proteção CSRF

Resultado esperado:

Requisições inválidas rejeitadas.

TS-005
Armazenamento de senha

Resultado esperado:

Hash seguro.

8. TESTES AJAX
TA-001
Load More Chamados

Validar:

paginação
JSON válido
Resultado:

Dados retornados corretamente.

TA-002
Detalhe Chamado AJAX

Validar:

resposta JSON
dados completos
Resultado:

Informações corretas.

9. TESTES DE USABILIDADE
Objetivo:

Garantir boa experiência do usuário.

TUX-001
Desktop

Resolução:

1920x1080

Resultado:

Layout correto.

TUX-002
Tablet

Resultado:

Layout responsivo.

TUX-003
Mobile

Resultado:

Navegação funcional.

10. TESTES DE PERFORMANCE
Objetivo:

Avaliar comportamento sob carga.

TP-001
Login

Meta:

< 2 segundos

TP-002
Listagem de Chamados

Meta:

< 2 segundos

TP-003
Dashboard TI

Meta:

< 3 segundos

TP-004
Consulta AJAX

Meta:

< 1 segundo

11. TESTES DE BANCO DE DADOS
TBD-001
Persistência de Chamado

Resultado:

Dados íntegros.

TBD-002
Persistência de Mensagem

Resultado:

Histórico preservado.

TBD-003
Integridade Referencial

Resultado:

Sem registros órfãos.

12. TESTES DE REGRESSÃO
Executados antes de cada release.

Checklist:

□ Login

□ Logout

□ Cadastro

□ Chamados

□ Chat

□ Dashboard

□ Relatórios

□ AJAX

13. CRITÉRIOS DE APROVAÇÃO
Release aprovada somente quando:

✓ 100% dos testes críticos aprovados

✓ Nenhum erro bloqueante

✓ Nenhum erro de segurança

✓ Nenhuma regressão crítica

14. COBERTURA DE TESTES
Meta Inicial:

60%

Meta Intermediária:

80%

Meta Corporativa:

90%

15. PIPELINE CI/CD FUTURO
Push GitHub

↓

Testes Unitários

↓

Testes Integração

↓

Testes Segurança

↓

Build

↓

Deploy

Ferramentas recomendadas:

GitHub Actions
Pytest
Coverage.py
Bandit
Ruff
16. MATRIZ DE RISCO
Área

Impacto

Prioridade

Login

Alto

Crítica

Permissões

Alto

Crítica

Chamados

Alto

Crítica

Chat

Médio

Alta

Relatórios

Médio

Média

Interface

Baixo

Baixa

17. DÉBITOS DE QUALIDADE IDENTIFICADOS
DQ-001

Arquivo tests.py praticamente vazio.

Impacto:

Ausência de validação automática.

DQ-002

Sem cobertura de testes.

Impacto:

Risco de regressão.

DQ-003

Sem pipeline CI/CD.

Impacto:

Deploys manuais.

DQ-004

Sem monitoramento de erros.

Impacto:

Baixa observabilidade.

18. ROADMAP DE QUALIDADE
Fase 1

Testes Unitários
Coverage
Fase 2

Integração
GitHub Actions
Fase 3

Segurança
Linting
Fase 4

Testes E2E
Fase 5

Observabilidade
Monitoramento
CONCLUSÃO
O Sistema de Chamados TICS possui uma base funcional sólida, porém sua maturidade de qualidade atualmente é dependente de testes manuais.

A adoção progressiva deste plano permitirá:

Redução de bugs
Releases mais seguras
Evolução previsível
Maior confiabilidade operacional
Preparação para ambientes corporativos de maior escala
FIM DO VOLUME V