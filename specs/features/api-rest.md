# REST API

Status: Planned

Objetivo:

Disponibilizar API REST.

Entidades:

- Usuario
- Chamado
- MensagemChat

Tecnologias:

- DRF
- JWT
- Swagger

Endpoints:

GET /api/chamados

POST /api/chamados

GET /api/chamados/{id}

POST /api/chamados/{id}/mensagens

Critérios:

- Autenticação JWT
- Permissões equivalentes ao frontend