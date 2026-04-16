# Implementation Plan: LinkAuto User, Booking and Scheduling Domains

**Branch**: `001-run-feature-hook` | **Date**: 2026-04-16 | **Spec**: `/specs/001-user-booking-domains/spec.md`
**Input**: Feature specification from `/specs/001-user-booking-domains/spec.md`

## Summary

Construir um MVP demo funcional para laboratorio de Engenharia de Software com fluxo
end-to-end Instrutor -> Admin -> Aluno -> Chat da Reserva, cobrindo os dominios de
usuarios, agenda, agendamento, mensagens, avaliacoes e notificacoes por e-mail.
Estrutura tecnica: monorepo com `linkauto-backend` (FastAPI + SQLAlchemy + Alembic)
e `linkauto-frontend` (React + Vite + Tailwind + ShadCN-ui + Leaflet), armazenamento
de documentos no S3, e regras de negocio RN02/RN03/RN04/RN05 validadas no backend
com reforco de UX no frontend.

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript ES2023 com React 19 (frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy, Alembic, Pydantic, boto3 (S3/SES), React, Vite, Tailwind CSS 4, ShadCN-ui, Leaflet, React Router DOM  
**Storage**: SQLite3 (dev), PostgreSQL + PostGIS (prod), AWS S3 para documentos de credenciamento  
**Testing**: pytest + httpx (backend), Vitest + Testing Library (frontend), smoke e2e do happy path  
**Target Platform**: Linux via Docker Compose para dev; web mobile-first para navegadores modernos  
**Project Type**: Web application monorepo (`linkauto-backend` + `linkauto-frontend`)  
**Performance Goals**: Busca geolocalizada <500ms em condicoes de prod; resposta de APIs criticas <300ms p95 em ambiente de demo  
**Constraints**: Sem pagamentos, sem WebSocket, minimo 2h por booking, cancelamento sem penalidade apenas >24h, review apenas apos `REALIZADA`, ids uuidv7 em novas entidades  
**Scale/Scope**: MVP demo de sala com dezenas de usuarios e centenas de registros de slots/bookings seeded

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Pre-Design Gate

- [x] No payment intermediation, transaction logging, or transaction value display introduced.
- [x] No real-time chat/WebSocket dependency introduced in V1.
- [x] Instructor visibility remains blocked until Admin validation.
- [x] Auth/security safeguards preserved where applicable: bcrypt passwords (no plain text), JWT access + refresh model.
- [x] LGPD credential-document lifecycle preserved: S3 documents deleted after validation.
- [x] Scheduling invariants preserved where applicable: 1h slots, minimum 2h booking, no overlaps.
- [x] Business rules preserved where applicable: penalty-free cancellation only with >24h notice; mutual rating only after status `REALIZADA`.
- [x] Stack remains compliant: React + Vite + Tailwind CSS 4 + ShadCN-ui + Leaflet; FastAPI + SQLAlchemy; SQLite dev; PostgreSQL + PostGIS prod; AWS S3 + SES.
- [x] Out-of-scope V1 guardrails preserved: no payments, no push/SMS/WhatsApp, no PDF/CSV export, no automated moderation, no instructor financial history.

Status: PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-user-booking-domains/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-v1-openapi.yaml
└── tasks.md                  # created by /speckit.tasks
```

### Source Code (repository root)

```text
linkauto-backend/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── schemas/
│   └── core/
├── alembic/
├── scripts/
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

linkauto-frontend/
├── src/
│   ├── app/
│   ├── pages/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   └── state/
└── tests/

infra/
└── docker-compose.yml
```

**Structure Decision**: Manter monorepo com diretorios existentes `linkauto-backend` e
`linkauto-frontend`, adicionando `infra/docker-compose.yml` para orquestracao local de
API, banco dev SQLite e Adminer.

## Phase 0 - Research Plan

1. Definir estrategia de infraestrutura local para demo (Compose, health check, seeds).
2. Validar padrao de concorrencia de reserva (first-write-wins atomico no backend).
3. Definir estrategia de geobusca: fallback por distancia em dev (SQLite) e PostGIS em prod.
4. Consolidar politica de ids uuidv7 para novas entidades.
5. Definir regras operacionais para automacoes (timeout 24h, realizacao +2h, penalidade 7 dias).

Output: `research.md`

## Phase 1 - Design and Contracts Plan

1. Modelar entidades e relacoes completas dos dominios de usuario, agenda, booking,
   mensagens, reviews e notificacoes.
2. Especificar constraints de negocio como invariantes de dados e transicoes de estado.
3. Definir contrato API v1 em OpenAPI com envelope padrao, erros e paginacao.
4. Escrever quickstart da demo com fluxo end-to-end Instrutor -> Admin -> Aluno -> Chat.
5. Atualizar contexto do agente para refletir stack e decisoes da feature.

Outputs: `data-model.md`, `contracts/api-v1-openapi.yaml`, `quickstart.md`

## Phase 2 - Implementation Strategy (for /speckit.tasks)

### Fase 0 - Fundacao

- Monorepo efetivo com backend/frontend conectados por contrato API.
- Docker Compose para API + SQLite dev + Adminer.
- Setup base FastAPI, SQLAlchemy, Alembic, env vars AWS/JWT e script de seed.

### Fase 1 - Autenticacao e Perfis

- Models: `User`, `StudentProfile`, `InstructorProfile`.
- Endpoints auth/me e fluxo de reset por SES.
- Upload de documentos do instrutor para S3 com status pendente.

### Fase 2 - Painel Admin

- Modelo `InstructorDocument` e workflow de aprovacao/rejeicao.
- Dashboard admin e notificacoes SES de decisao.

### Fase 3 - Agenda e Busca

- Modelo `Slot` com janela fixa de 1h.
- Busca geolocalizada com filtros e mapa Leaflet.

### Fase 4 - Agendamento

- Modelo `Booking` + state machine.
- Validacoes RN02/RN03/RN04 e timeout automatico em 24h.

### Fase 5 - Chat da Reserva e Avaliacoes

- Modelo `BookingMessage` para thread assincrona por booking.
- Modelo `Review` liberado apenas apos `REALIZADA`.

### Fase 6 - Polimento e Demo Prep

- Hardening UX (loading/error/empty), responsividade, seed final e roteiro de demo.

## Constitution Check (Post-Design)

- [x] Design manteve mensagens assincronas sem WebSocket.
- [x] Design manteve ausencia de pagamentos/intermediacao financeira.
- [x] Fluxo de credenciamento exige aprovacao admin antes de visibilidade em busca.
- [x] Design inclui exclusao de documentos do S3 apos validacao.
- [x] RN02/RN03/RN04/RN05 foram traduzidas para invariantes de dominio e contrato.
- [x] Stack proposta permanece dentro do baseline constitucional.

Status: PASS

## Complexity Tracking

Sem violacoes constitucionais que exijam justificativa.
