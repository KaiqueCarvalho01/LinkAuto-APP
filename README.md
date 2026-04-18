![LinkAuto Logo](docs/images/LinkAuto-logo-square.webp)

Plataforma mobile-first para conectar alunos e instrutores autonomos de transito.

Idioma:

- PT-BR: [README.md](README.md)
- US-EN: [docs/README.en.md](docs/README.en.md)

Navegacao rapida:

- [Visao geral](#visao-geral)
- [Status atual](#status-atual)
- [Como executar](#como-executar-localmente)
- [Qualidade e testes](#qualidade-e-testes)

![LinkAuto Banner](docs/images/LinkAuto-banner.webp)

> [!IMPORTANT]
> Este README descreve o estado atual do codigo neste repositorio.
> O source-of-truth funcional e contratual da feature V1 esta em specs/001-user-booking-domains.

## Visao geral

O LinkAuto organiza o fluxo de descoberta de instrutores, autenticacao, validacao administrativa e (na proxima fase) agendamento completo com regras de negocio para Booking.

Escopo funcional consolidado da V1:

- Usuario multi-role (ALUNO, INSTRUTOR, ADMIN)
- Fluxo de autenticacao com access token + refresh token via cookie
- Validacao administrativa de instrutor
- Upload de documentos de credenciamento com validacoes de seguranca
- Contrato OpenAPI para slots, booking, mensagens e reviews

Referencias principais:

- [specs/001-user-booking-domains/spec.md](specs/001-user-booking-domains/spec.md)
- [specs/001-user-booking-domains/plan.md](specs/001-user-booking-domains/plan.md)
- [specs/001-user-booking-domains/tasks.md](specs/001-user-booking-domains/tasks.md)
- [specs/001-user-booking-domains/contracts/api-v1-openapi.yaml](specs/001-user-booking-domains/contracts/api-v1-openapi.yaml)

## Status atual

### Progresso por fase

| Fase | Estado |
| --- | --- |
| Phase 1 - Setup | Concluida |
| Phase 2 - Foundational | Concluida |
| Phase 3 - US1 | Concluida |
| Phase 4 - US2 | Pendente |
| Phase 5 - US3 | Pendente |
| Phase 6 - Polish | Pendente |

### O que ja esta implementado

Backend:

- FastAPI com roteamento versionado em /api/v1 e healthcheck em /health
- Envelopes padronizados de sucesso/erro e tratamento de validacao
- JWT access/refresh, RBAC e refresh token em cookie HttpOnly/Secure/SameSite
- Fluxo US1 completo: registro, login, profile, listagem publica de instrutores aprovados
- Painel admin para aprovar/rejeitar instrutores
- Upload de documentos com limite de 10MB e whitelist MIME (PDF/JPEG/PNG)
- Catalogo de notificacoes v1 (gateway em memoria no estado atual)

Frontend:

- React 19 + Vite com rotas protegidas por sessao e papel
- Fluxos conectados para login, profile e painel admin de validacao de instrutores
- Cliente HTTP com cookies, bearer token e tratamento de erro padronizado

> [!NOTE]
> O runtime atual de US1 utiliza store em memoria (IdentityStore), adequado para validacao de contratos e testes de fluxo.
> As fases US2/US3 completam persistencia e regras de Booking end-to-end.

## Contrato vs runtime

O contrato OpenAPI ja descreve endpoints de slots, booking, mensagens e reviews.
No runtime atual, os endpoints operacionais sao:

- /health
- /api/v1/foundation/*
- /api/v1/auth/*
- /api/v1/users/me
- /api/v1/users/public-instructors
- /api/v1/admin/instructors*
- /api/v1/instructors/{id}/documents

## Arquitetura e stack

- Frontend: React 19, Vite, Tailwind CSS 4, React Router, Leaflet (mapas) e ShadCN/UI (componentes)
- Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic
- Banco: SQLite (dev) e PostgreSQL + PostGIS (alvo de producao)
- Integracoes: AWS S3 (documentos) e AWS SES (notificacoes)

Diagramas disponiveis:

- [docs/diagrams/architecture-overview.svg](docs/diagrams/architecture-overview.svg)
- [docs/diagrams/use-cases-v1.svg](docs/diagrams/use-cases-v1.svg)
- [docs/diagrams/uml-class-diagram-v1.svg](docs/diagrams/uml-class-diagram-v1.svg)
- [docs/diagrams/booking-sequence.svg](docs/diagrams/booking-sequence.svg)

## Estrutura do repositorio

```text
.
├── docs/
├── infra/
├── linkauto-backend/
├── linkauto-frontend/
├── specs/
│   └── 001-user-booking-domains/
└── README.md
```

## Como executar localmente

### Opcao A (recomendada): Docker Compose

```bash
docker compose -f infra/docker-compose.yml up -d
```

Servicos:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### Opcao B: Backend e frontend separados

Backend:

```bash
cd linkauto-backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd linkauto-frontend
npm install
npm run dev
```

> [!TIP]
> Se voce for validar fluxo de auth com refresh cookie, mantenha frontend e backend rodando com credentials habilitado (ja configurado no cliente HTTP).

## Qualidade e testes

Backend (contrato + integracao):

```bash
cd linkauto-backend
. .venv/bin/activate
ruff check .
pytest
```

Frontend (qualidade basica):

```bash
cd linkauto-frontend
npm run lint
npm run build
```

Coberturas relevantes ja presentes:

- Contrato base de envelope/auth/conflict
- Contrato e fluxo de auth + users/me
- State machine de Booking (dominio)
- Validacao de upload (MIME/10MB)
- Visibilidade de instrutor aprovada por admin

## Roadmap imediato

Itens das proximas fases:

- US2: slots, booking, penalties, conflitos e override administrativo de booking
- US3: mensagens por booking, reviews apos REALIZADA e eventos de notificacao completos
- Polish: hardening, regressao em cascata no Booking core e validacao final

Regra de execucao por dependencia:

User -> Profile -> Slot -> Booking -> BookingMessage -> Review
