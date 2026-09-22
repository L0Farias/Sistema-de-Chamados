# Integração Google Calendar — Guia de Configuração

## Visão geral

O sistema verifica automaticamente conflitos de horário no Google Calendar ao criar um novo agendamento de multimídia. Se o local solicitado estiver ocupado, o agendamento é bloqueado antes de ser salvo no banco de dados.

---

## Pré-requisitos

- Conta Google (pode ser a conta institucional)
- Acesso ao [Google Cloud Console](https://console.cloud.google.com/)

---

## Passo 1 — Criar projeto no Google Cloud

1. Acesse https://console.cloud.google.com/
2. Clique em **Select a project** → **New Project**
3. Dê um nome ao projeto (ex: `TICS-Agendamentos`)
4. Clique em **Create**

---

## Passo 2 — Ativar a API Google Calendar

1. No painel do projeto, vá em **APIs & Services > Library**
2. Pesquise por **Google Calendar API**
3. Clique em **Enable**

---

## Passo 3 — Criar uma Service Account

Uma Service Account permite que o servidor Django acesse o Google Calendar sem precisar de login interativo.

1. Vá em **IAM & Admin > Service Accounts**
2. Clique em **Create Service Account**
3. Preencha:
   - Nome: `tics-agendamentos`
   - ID: gerado automaticamente
4. Clique em **Create and Continue**
5. Em **Grant this service account access to project**, clique em **Continue** (sem papéis necessários por enquanto)
6. Clique em **Done**

---

## Passo 4 — Gerar a chave JSON

1. Na lista de Service Accounts, clique na conta criada
2. Vá na aba **Keys**
3. Clique em **Add Key > Create new key**
4. Selecione **JSON**
5. Clique em **Create**
6. O arquivo JSON será baixado automaticamente

> ⚠️ **IMPORTANTE**: Este arquivo contém credenciais privadas.
> - **Nunca adicione ao Git**
> - **Nunca compartilhe publicamente**
> - Salve em local seguro fora do repositório

---

## Passo 5 — Criar o Calendário

1. Acesse https://calendar.google.com/
2. Na barra lateral esquerda, clique em **+** ao lado de "Other calendars"
3. Selecione **Create new calendar**
4. Nome: `Agendamentos TICS`
5. Clique em **Create calendar**

---

## Passo 6 — Compartilhar o Calendário com a Service Account

1. No Google Calendar, clique nos três pontos ao lado do calendário criado
2. Selecione **Settings and sharing**
3. Role até **Share with specific people or groups**
4. Clique em **+ Add people and groups**
5. Cole o **e-mail da Service Account** (formato: `nome@projeto.iam.gserviceaccount.com`)
6. Em **Permissions**, selecione **Make changes to events**
7. Clique em **Send**

---

## Passo 7 — Obter o ID do Calendário

1. Nas configurações do calendário (passo 6), role até **Integrate calendar**
2. Copie o valor em **Calendar ID**
   - Exemplo: `c_abc123xyz@group.calendar.google.com`

---

## Passo 8 — Configurar o .env

Abra o arquivo `.env` do projeto e adicione:

```env
GOOGLE_SERVICE_ACCOUNT_FILE=/caminho/absoluto/para/service_account.json
GOOGLE_CALENDAR_ID=seu-calendario@group.calendar.google.com
```

**Exemplos reais (não commitar):**

```env
GOOGLE_SERVICE_ACCOUNT_FILE=/home/usuario/credenciais/tics-sa.json
GOOGLE_CALENDAR_ID=c_abc123def456@group.calendar.google.com
```

---

## Comportamento sem configuração

Se `GOOGLE_SERVICE_ACCOUNT_FILE` ou `GOOGLE_CALENDAR_ID` **não estiverem definidos** no `.env`, o sistema funcionará normalmente, **mas sem verificação de conflitos**.

Os agendamentos serão criados diretamente no banco sem consultar o Google Calendar.

Isso é útil para desenvolvimento local sem credenciais configuradas.

---

## Fluxo com integração ativa

```
Usuário → Novo Agendamento
          ↓
    Django valida formulário
          ↓
    Consulta Google Calendar
     (local + data + horário)
          ↓
    Conflito encontrado?
    ↙              ↘
  SIM              NÃO
   ↓                ↓
Rejeita        Cria evento no
agendamento    Google Calendar
   ↓                ↓
Mensagem       Recebe event_id
de conflito         ↓
               Salva agendamento
               no Django
```

---

## Locais disponíveis

Os únicos locais aceitos pelo sistema são:

| # | Local |
|---|-------|
| 1 | Auditório da Prefeitura |
| 2 | Sede da Secretaria de Saúde |
| 3 | Centro Integrado |
| 4 | Faetec |
| 5 | Sicoob |
| 6 | Ciep |
| 7 | Maristas |
| 8 | Cipec |
| 9 | Sala dos Conselhos |

Não é possível digitar um local manualmente — o campo é um `<select>` com as opções acima.

---

## Segurança

- O arquivo JSON de credenciais **nunca deve ser commitado**
- O `.gitignore` já protege: `.env`, `*service_account*.json`, `*credentials*.json`
- O usuário comum nunca visualiza os eventos do Google Calendar diretamente
- O usuário comum recebe apenas: "Disponível" ou "Horário indisponível"

---

## Execução dos testes

Os testes **não dependem** de credenciais reais — usam mocks:

```bash
python manage.py test chamados.tests.test_google_calendar
```

Resultado esperado: `Ran 18 tests in X.Xs — OK`
