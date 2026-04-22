# Implementation Plan: Frontend Iterative Delivery Guardrails

**Branch**: `001-frontend-polishment` | **Date**: 2026-04-21 | **Spec**: `/specs/002-frontend-iterative-spec/spec.md`
**Input**: Feature specification from `/specs/002-frontend-iterative-spec/spec.md`

## Summary

Padronizar a execucao das iteracoes frontend em fatias pequenas (maximo 4 tasks ou 1 feature de user story), com disciplina XP/TDD red-green obrigatoria, cobertura minima de 80% por fatia alterada e rastreabilidade em markdown. O plano reforca fronteiras de integracao com backend em brownfield, oficializa mock-first para dependencias nao contratadas e exige justificativa documentada antes de qualquer demanda de novo endpoint.

## Technical Context

**Language/Version**: TypeScript 5.9, React 19.2, Markdown para artefatos de processo  
**Primary Dependencies**: React, Chakra UI v3, Tailwind CSS 4, React Router DOM 7, Leaflet/react-leaflet, Lucide React  
**Storage**: N/A para funcionalidade de processo; persistencia dos artefatos em arquivos markdown no repositorio  
**Testing**: Vitest + Testing Library (unit/integration UI), Playwright (e2e), red-green por task  
**Target Platform**: Aplicacao web frontend (desktop/mobile browsers) em ambiente de dev Linux  
**Project Type**: Web application (frontend stream em repositorio brownfield fullstack)  
**Performance Goals**: Sem regressao funcional na navegacao principal; 0 links/rotas quebrados por iteracao; manter baseline atual de build e testes aprovados  
**Constraints**: Maximo 4 tasks ou 1 feature por ciclo; cobertura >=80% por escopo alterado; atualizacao obrigatoria de markdown tracker por iteracao; branch atual mantida  
**Scale/Scope**: Governanca de entrega para iteracoes FE-001..FE-008 da landing e evolucoes frontend subsequentes no mesmo fluxo

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Pre-Phase 0 gate:

- [x] No payment intermediation, transaction logging, or transaction value display introduced.
- [x] No real-time chat/WebSocket dependency introduced in V1.
- [x] Instructor visibility remains blocked until Admin validation.
- [x] Auth/security safeguards preserved where applicable: bcrypt passwords (no plain text), JWT access + refresh model.
- [x] LGPD credential-document lifecycle preserved: S3 documents deleted after validation.
- [x] Scheduling invariants preserved where applicable: 1h slots, minimum 2h booking, no overlaps.
- [x] Business rules preserved where applicable: penalty-free cancellation only with >24h notice; mutual rating only after status `REALIZADA`.
- [x] Stack remains compliant with approved V1 baseline; this feature does not introduce new runtime stack changes.
- [x] Out-of-scope V1 guardrails preserved: no payments, no push/SMS/WhatsApp, no PDF/CSV export, no automated moderation, no instructor financial history.

Post-Phase 1 re-check:

- [x] Research and design artifacts preserve all constitutional constraints.
- [x] No gate violations introduced by data model, quickstart workflow, or contracts.

## Project Structure

### Documentation (this feature)

```text
specs/002-frontend-iterative-spec/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── frontend-iteration-governance.md
├── endpoint-requests.md
└── tasks.md                     # generated later by /speckit.tasks
```

### Source Code (repository root)

```text
docs/
├── DESIGN.md
└── designs/
    └── landpage_UX.md

linkauto-frontend/
├── src/
│   ├── app/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── state/
│   └── test/
├── tests/
│   └── e2e/
├── vitest.config.ts
└── playwright.config.ts

linkauto-backend/
└── app/

progressTracker-frontend.md
```

**Structure Decision**: Manter o monorepo existente com stream frontend separado por artefatos markdown em `specs/002-frontend-iterative-spec/` e rastreio operacional em `progressTracker-frontend.md`, sem criar novo acoplamento estrutural com backend.

## Complexity Tracking

No constitutional violations or justified complexity exceptions were identified in this plan.
