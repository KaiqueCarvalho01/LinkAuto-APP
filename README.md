![LinkAuto Banner](/docs/images/LinkAuto-banner.webp)

Plataforma mobile-first para conectar alunos e instrutores de transito autonomos.
Mobile-first platform to connect students and autonomous driving instructors.

> [!IMPORTANT]
> Estado atual do projeto: a implementacao completa dos dominios backend ainda nao comecou de forma definitiva.
> Este repositorio ja contem o source-of-truth consolidado da V1 via Spec Kit em specs/001-user-booking-domains.

## Language / Idioma

- PT-BR: [Ir para secao em Portugues](#pt-br)
- US-EN: [Go to English section](#us-en)

---

## PT-BR

### Visao Geral

O LinkAuto e uma plataforma web mobile-first para descoberta, agendamento e reputacao entre alunos e instrutores autonomos credenciados.

Escopo consolidado para a V1:

- Busca de instrutores aprovados com filtros e geolocalizacao
- Reserva de aulas com regras de agenda e ciclo de vida de booking
- Mensagens assincronas por booking
- Avaliacao mutua apos status REALIZADA
- Notificacoes por e-mail
- Validacao administrativa de credenciamento

> [!NOTE]
> Os requisitos e decisoes mais atualizados devem ser lidos primeiro em:
>
> - [specs/001-user-booking-domains/spec.md](specs/001-user-booking-domains/spec.md)
> - [specs/001-user-booking-domains/plan.md](specs/001-user-booking-domains/plan.md)
> - [specs/001-user-booking-domains/tasks.md](specs/001-user-booking-domains/tasks.md)
> - [specs/001-user-booking-domains/contracts/api-v1-openapi.yaml](specs/001-user-booking-domains/contracts/api-v1-openapi.yaml)

### Escopo V1 e Guardrails

Incluido na V1:

- Fluxo principal: busca -> selecao -> booking -> confirmacao -> realizacao -> avaliacao
- Slots de 1h e booking minimo de 2h
- Concorrencia de booking com first-write-wins e resposta de conflito
- Refresh token via cookie HttpOnly/Secure/SameSite
- Upload de documentos com limite de 10MB e whitelist MIME

Fora do escopo V1:

- Intermediacao/processamento de pagamentos
- Chat em tempo real (WebSocket)
- Push/SMS/WhatsApp
- Exportacao PDF/CSV
- Moderacao automática de avaliações

### Status Atual do Repositorio

- Backend: estrutura planejada e documentada, sem implementacao definitiva de dominios ainda
- Frontend: base React + Vite existente com paginas/componentes iniciais
- Contrato API: definido em OpenAPI 3.1 para os fluxos centrais da V1
- Planejamento: backlog por historias e gates de estabilidade por fase

### Arquitetura e Diagramas (Placeholders)

Os diagramas serao adicionados posteriormente para suportar implementacao e onboarding.

| Artefato | Status | Diagrama |
| --- | --- | --- |
| Diagrama de Arquitetura | Concluído | ![Diagrama de Arquitetura](docs/diagrams/architecture-overview.svg) |
| Diagrama de Casos de Uso | Concluído |![Diagrama de Casos de Uso](docs/diagrams/use-cases-v1.svg) |
| Diagrama de Classes | Concluído | ![Diagrama de Classes](docs/diagrams/uml-class-diagram-v1.svg) |
| Diagrama de Sequencia (Booking) | Concluído | ![Diagrama de Sequencia](docs/diagrams/booking-sequence.svg) |

> [!TIP]
> Quando os diagramas forem adicionados, mantenha-os alinhados com spec, plan, tasks e contrato para evitar divergencia de documentacao.

### Stack Tecnica Consolidada

- Frontend: React 19, Vite, Tailwind CSS 4, ShadCN-ui, Leaflet
- Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic
- Banco dev: SQLite3
- Banco prod: PostgreSQL + PostGIS
- Storage: AWS S3
- Email: AWS SES
- Autenticacao: JWT access + refresh token por cookie

### Estrutura do Projeto

```text
.
├── docs/
├── linkauto-backend/
├── linkauto-frontend/
├── specs/
│   └── 001-user-booking-domains/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md
│       └── contracts/
│           └── api-v1-openapi.yaml
└── README.md
```

### Como Executar (Estado Atual)

Hoje, o que esta pronto para execucao direta no workspace e o frontend base.

Pre-requisitos:

- Node.js 20+

Passos:

```bash
cd linkauto-frontend
npm install
npm run dev
```

### Execucao Planejada da Stack Completa (Referencia)

Com base no quickstart consolidado da feature, a stack completa sera executada com backend, migracoes e seed.

```bash
docker compose -f infra/docker-compose.yml up -d
cd linkauto-backend
alembic upgrade head
python scripts/seed_demo.py

cd ../linkauto-frontend
npm install
npm run dev
```

Referencia: [specs/001-user-booking-domains/quickstart.md](specs/001-user-booking-domains/quickstart.md)

### Processo de Implementacao

Este repositorio segue fluxo orientado por especificacao com gates de estabilidade por fase.

Ordem de dependencia de dominio:

User -> Profile -> Slot -> Booking -> BookingMessage -> Review

Regra central:

- Booking e o nucleo do sistema; qualquer mudanca nele exige regressao em cascata antes de avancar de fase.

---

## US-EN

### Overview

LinkAuto is a mobile-first web platform for discovery, scheduling, and reputation workflows between students and autonomous driving instructors.

Consolidated V1 scope:

- Approved instructor search with filters and geolocation
- Lesson booking with scheduling/business lifecycle rules
- Asynchronous booking-bound messages
- Mutual review after REALIZADA status
- Email notifications
- Admin credential validation workflow

> [!NOTE]
> The current source-of-truth for V1 must be read first in:
>
> - [specs/001-user-booking-domains/spec.md](specs/001-user-booking-domains/spec.md)
> - [specs/001-user-booking-domains/plan.md](specs/001-user-booking-domains/plan.md)
> - [specs/001-user-booking-domains/tasks.md](specs/001-user-booking-domains/tasks.md)
> - [specs/001-user-booking-domains/contracts/api-v1-openapi.yaml](specs/001-user-booking-domains/contracts/api-v1-openapi.yaml)

### V1 Scope and Guardrails

Included in V1:

- Main flow: search -> selection -> booking -> confirmation -> completion -> review
- 1-hour slots and 2-hour minimum booking
- Booking concurrency with first-write-wins and conflict semantics
- Refresh token via HttpOnly/Secure/SameSite cookie
- Credential upload with 10MB limit and MIME whitelist

Out of scope for V1:

- Payment processing/intermediation
- Real-time chat (WebSocket)
- Push/SMS/WhatsApp notifications
- PDF/CSV export
- Automated review moderation

### Current Repository Status

- Backend: planned and documented structure, domain implementation not fully started yet
- Frontend: existing React + Vite base with initial pages/components
- API contract: OpenAPI 3.1 defined for core V1 flows
- Planning: user-story backlog with mandatory phase stability gates

### Architecture and Diagrams (Placeholders)

Diagrams will be added later to support implementation and onboarding.

| Artifact | Status | Suggested path |
| --- | --- | --- |
| Architecture Diagram | Done | ![Architecture Diagram](docs/diagrams/architecture-overview.svg) |
| Use Case Diagram | Done | ![Use Case Diagram](docs/diagrams/use-cases-v1.svg) |
| UML Class Diagram | Done | ![UML Class Diagram](docs/diagrams/uml-class-diagram-v1.svg) |
| Booking Sequence Diagram | Done | ![Booking Sequence Diagram](docs/diagrams/booking-sequence.svg) |

> [!TIP]
> Keep all diagrams synchronized with spec, plan, tasks, and contract to avoid documentation drift.

### Consolidated Technical Stack

- Frontend: React 19, Vite, Tailwind CSS 4, ShadCN-ui, Leaflet
- Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic
- Dev database: SQLite3
- Prod database: PostgreSQL + PostGIS
- Storage: AWS S3
- Email: AWS SES
- Auth: JWT access + cookie-based refresh token

### Project Structure

```text
.
├── docs/
├── linkauto-backend/
├── linkauto-frontend/
├── specs/
│   └── 001-user-booking-domains/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md
│       └── contracts/
│           └── api-v1-openapi.yaml
└── README.md
```

### Run Instructions (Current State)

At the moment, the directly runnable part in this workspace is the frontend base.

Prerequisites:

- Node.js 20+

Steps:

```bash
cd linkauto-frontend
npm install
npm run dev
```

### Planned Full-Stack Run Flow (Reference)

Based on the consolidated feature quickstart, full-stack execution will include backend services, migrations, and seed.

```bash
docker compose -f infra/docker-compose.yml up -d
cd linkauto-backend
alembic upgrade head
python scripts/seed_demo.py

cd ../linkauto-frontend
npm install
npm run dev
```

Reference: [specs/001-user-booking-domains/quickstart.md](specs/001-user-booking-domains/quickstart.md)

### Implementation Process

This repository follows a specification-driven workflow with mandatory phase stability gates.

Domain dependency order:

User -> Profile -> Slot -> Booking -> BookingMessage -> Review

Core rule:

- Booking is the core aggregate; any change requires cascade regression validation before phase progression.
