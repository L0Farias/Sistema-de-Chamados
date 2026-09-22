# Sistema-de-Chamados

# 🖥️ Sistema de Chamados TICS

Sistema web para **gerenciamento de chamados de suporte de Tecnologia da Informação**, desenvolvido para centralizar solicitações, organizar o atendimento da equipe de TI e acompanhar o ciclo de vida dos chamados.

O projeto foi desenvolvido com **Django** e utiliza uma arquitetura web baseada em MVT, com interface responsiva utilizando Bootstrap.

---

## 📌 Sobre o projeto

O **Sistema de Chamados TICS** foi desenvolvido para substituir processos descentralizados de atendimento, como solicitações realizadas por planilhas, WhatsApp, e-mails e outros meios informais.

A aplicação centraliza o registro e acompanhamento dos chamados em um único ambiente, permitindo que usuários solicitem suporte e que a equipe responsável faça a triagem, atendimento e encerramento das solicitações.

Além do gerenciamento tradicional de chamados, o sistema possui funcionalidades para **agendamento de recursos multimídia e integração com o Google Calendar**.

---

## ✨ Funcionalidades

### 🎫 Gerenciamento de chamados

* Criação de chamados pelos usuários
* Visualização dos chamados do usuário
* Triagem de solicitações
* Atribuição de atendentes
* Alteração de status
* Atendimento dos chamados
* Encerramento e reabertura
* Histórico e acompanhamento das solicitações
* Sistema de mensagens relacionado aos chamados

### 📊 Fluxo de atendimento

Os chamados seguem um fluxo organizado:

```text
┌─────────┐
│   Novo  │
└────┬────┘
     ↓
┌─────────┐
│ Triagem │
└────┬────┘
     ↓
┌────────────────┐
│ Em Atendimento │
└───────┬────────┘
        ↓
┌──────────┐
│ Fechado  │
└──────────┘
```

Chamados fechados também podem ser reabertos quando necessário.

---

### 📅 Agendamento multimídia

O sistema permite realizar solicitações relacionadas ao uso de recursos multimídia.

Entre os recursos implementados estão:

* Cadastro de agendamentos
* Seleção de local
* Data e horário
* Descrição da atividade
* Visualização dos agendamentos
* Gerenciamento dos agendamentos
* Integração com Google Calendar

---

### 🔗 Google Calendar

O sistema possui integração com o **Google Calendar**, permitindo sincronizar os agendamentos cadastrados na aplicação com um calendário externo.

A integração foi desenvolvida de forma isolada através de um serviço específico:

```text
chamados/
└── services/
    └── google_calendar.py
```

As instruções de configuração estão disponíveis em:

```text
docs/google_calendar_setup.md
```

---

### 👤 Usuários

O sistema possui diferentes níveis de utilização, permitindo separar funcionalidades de acordo com o perfil do usuário.

Entre os recursos disponíveis:

* Autenticação
* Login
* Controle de acesso
* Área do usuário
* Área de gerenciamento
* Configurações do usuário

---

## 🧪 Testes

O projeto possui testes automatizados relacionados à integração com o Google Calendar.

Localização:

```text
chamados/tests/
└── test_google_calendar.py
```

Para executar os testes:

```bash
python manage.py test
```

---

## 🛠️ Tecnologias utilizadas

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge\&logo=django\&logoColor=white)

### Frontend

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge\&logo=html5\&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge\&logo=css3\&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge\&logo=bootstrap\&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge\&logo=javascript\&logoColor=black)

### Banco de dados

![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white)

### Integrações

![Google Calendar](https://img.shields.io/badge/Google%20Calendar-4285F4?style=for-the-badge\&logo=googlecalendar\&logoColor=white)

### Ferramentas

![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge\&logo=git\&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge\&logo=github\&logoColor=white)

---

## 🏗️ Arquitetura

O projeto utiliza a arquitetura **MVT (Model-View-Template)** do Django.

```text
                    ┌──────────────────┐
                    │     Usuário      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Templates    │
                    │  HTML / Bootstrap│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      Views       │
                    │  Regras / Fluxos │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │      Models     │       │     Services    │
       │     Django ORM  │       │  Google Calendar│
       └────────┬────────┘       └────────┬────────┘
                │                         │
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │     SQLite      │       │ Google Calendar │
       └─────────────────┘       └─────────────────┘
```

---

## 📁 Estrutura do projeto

```text
Chamados de TI Django/
│
├── chamados/
│   ├── migrations/
│   │   └── 0009_agendamento_google_calendar.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── google_calendar.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_google_calendar.py
│   │
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── docs/
│   └── google_calendar_setup.md
│
├── specs/
│   └── ...
│
├── .kiro/
│   └── specs/
│
├── templates/
│   └── chamados/
│       ├── agendamento_multimidia.html
│       ├── configuracoes_usuario.html
│       ├── criar_chamado.html
│       ├── meus_agendamentos.html
│       ├── novo_agendamento.html
│       └── usuario_comum.html
│
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/L0Farias/Sistema-de-Chamados.git
```

Entre na pasta:

```bash
cd Sistema-de-Chamados
```

---

### 2. Crie um ambiente virtual

Windows:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

Depois abra o `.env` e configure os valores necessários.

> ⚠️ Nunca envie o arquivo `.env` para o GitHub. Ele pode conter informações sensíveis e credenciais.

---

### 5. Execute as migrações

```bash
python manage.py migrate
```

---

### 6. Crie um usuário administrador

```bash
python manage.py createsuperuser
```

---

### 7. Inicie o servidor

```bash
python manage.py runserver
```

A aplicação estará disponível localmente em:

```text
http://127.0.0.1:8000/
```

---

## 📅 Configuração do Google Calendar

A integração com o Google Calendar exige configuração adicional das credenciais e da API.

As instruções completas estão disponíveis em:

```text
docs/google_calendar_setup.md
```

A configuração deve ser realizada utilizando variáveis de ambiente e credenciais apropriadas.

**Nunca coloque credenciais reais diretamente no código-fonte.**

---

## 🧪 Executando os testes

Para executar toda a suíte de testes:

```bash
python manage.py test
```

Para executar especificamente os testes do Google Calendar:

```bash
python manage.py test chamados.tests.test_google_calendar
```

---

## 📚 Desenvolvimento orientado por especificações

O projeto utiliza uma abordagem de **Spec-Driven Development (SDD)** para organizar a evolução das funcionalidades.

As especificações ficam organizadas em:

```text
.kiro/specs/
```

e:

```text
specs/
```

A documentação auxilia no planejamento e rastreabilidade das funcionalidades, requisitos e decisões técnicas.

---

## 🗺️ Organização do desenvolvimento

O desenvolvimento é organizado em etapas, contemplando:

```text
Requisitos
    ↓
Especificação
    ↓
Implementação
    ↓
Testes
    ↓
Documentação
    ↓
Validação
```

---

## 🔐 Segurança

O projeto utiliza algumas práticas básicas para evitar o versionamento de informações sensíveis:

* `.env` ignorado pelo Git
* Credenciais externas ignoradas
* Arquivos de service account ignorados
* Variáveis sensíveis configuradas por ambiente
* `.env.example` disponibilizado como referência

Arquivos como:

```text
.env
*service_account*.json
*credentials*.json
*google_credentials*.json
```

não devem ser enviados ao repositório.

---

## 📖 Documentação

Documentações adicionais podem ser encontradas em:

```text
docs/
```

Atualmente:

```text
docs/
└── google_calendar_setup.md
```

As especificações técnicas relacionadas ao desenvolvimento também estão disponíveis no diretório:

```text
.kiro/specs/
```

---

## 🔄 Fluxo Git

O projeto utiliza Git para controle de versão.

Exemplo de fluxo:

```bash
git pull

# realizar alterações

git add .

git commit -m "feat: descrição da alteração"

git push origin main
```

### Convenção de commits

Sempre que possível, utilize mensagens seguindo o padrão:

```text
feat: nova funcionalidade
fix: correção de problema
docs: atualização de documentação
test: adição ou alteração de testes
refactor: refatoração de código
chore: manutenção do projeto
```

---

## 📌 Status do projeto

🚧 **Em desenvolvimento**

O sistema continua recebendo melhorias, novas funcionalidades, testes e refinamentos arquiteturais.

---

## 👨‍💻 Autor

**Lucas Freitas Farias**

Desenvolvedor / Estudante de Engenharia de Software

GitHub:

**[@L0Farias](https://github.com/L0Farias)**

---

## 📄 Licença

Este projeto está em desenvolvimento e a definição da licença pode ser adicionada conforme a política de distribuição adotada para o sistema.

---

<p align="center">
  Desenvolvido com Python e Django 💻
</p>
