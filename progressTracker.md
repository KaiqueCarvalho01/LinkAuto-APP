# progressTracker

## Contexto

Rastreamento incremental da implementação da feature `001-user-booking-domains`.

## Status por fase

| Fase | Estado | Observação |
| ------ | -------- | ------------ |
| Phase 1 - Setup | Concluída | T001-T006 finalizadas |
| Phase 2 - Foundational | Concluída | T007-T017 finalizadas e validadas |
| Phase 3 - US1 | Concluída | T018-T029 + T056/T057 finalizadas |
| Phase 4 - US2 | Em andamento | Frontend US2 preview concluído; infraestrutura DEV/e2e iniciada |
| Phase 5 - US3 | Pendente | Bloqueada por dependência |
| Phase 6 - Polish | Pendente | Bloqueada por dependência |

## Iterações

### Iteração 1

- Criados arquivos de ignore e ajustes de lint ignore.
- Criado esqueleto inicial do backend (app/core/api/models/services/schemas).
- Criado bootstrap de runtime (`infra/docker-compose.yml`) e arquivos `.env.example`.
- Criado cliente HTTP base no frontend (`src/services/httpClient.js` + `config.js`).
- Criado bootstrap Alembic (`alembic/env.py` + `0001_foundation.py`).
- Criado `specs/001-user-booking-domains/compliance.md`.

### Iteração 2

- Implementado `app/models/base.py` com mixins de `uuidv7` (com fallback) e timestamps de auditoria.
- Implementados envelopes/paginação/erros em `app/schemas/common.py`.
- Implementados hashing bcrypt e tokens JWT access/refresh em `app/core/security.py`.
- Implementadas dependências de autenticação e RBAC em `app/api/deps/authn.py` e `authz.py`.
- Implementada abstração de notificação com adapter SES em `app/services/notification_service.py`.
- Implementado core do domínio Booking (matriz de transição + guards) em `app/domain/booking.py`.
- Implementado serviço de reserva atômica first-write-wins em `app/services/booking_lock_service.py`.
- Implementado shell de automações de booking (timeout 24h e +2h completion) em `app/services/booking_scheduler.py`.
- Implementado roteamento fundacional V1 em `app/api/v1/__init__.py` e tratamento padronizado de erro em `app/main.py`.
- Adicionados testes fundacionais de contrato e integração:
  - `tests/contract/test_foundation_contract.py`
  - `tests/integration/test_booking_state_machine.py`

### Iteração 3

- US1 backend implementado com testes:
  - `tests/contract/test_us1_auth_profile_contract.py`
  - `tests/integration/test_us1_profiles_visibility.py`
  - `tests/integration/test_us1_document_upload_validation.py`
- Modelos de domínio US1 adicionados:
  - `app/models/user.py`
  - `app/models/instructor_document.py`
- Serviços US1 adicionados:
  - `app/services/auth_service.py`
  - `app/services/profile_service.py`
  - `app/services/admin_validation_service.py`
  - `app/services/document_cleanup_service.py`
  - `app/services/instructor_document_service.py`
  - `app/services/us1_store.py`
- Endpoints US1 adicionados/organizados:
  - `app/api/v1/auth.py`
  - `app/api/v1/users.py`
  - `app/api/v1/admin_instructors.py`
  - `app/api/v1/instructor_documents.py`
- Frontend US1 conectado à API:
  - login com backend (`src/pages/Login.jsx`)
  - perfil com sessão (`src/pages/Profile.jsx`)
  - painel admin para validação (`src/pages/InstructorDashboard.jsx`)
  - session store e guards por papel (`src/state/sessionStore.js`, `src/app/router.jsx`)

### Iteração 4

- Frontend expandido para preview US2 com identidade visual alinhada ao `docs/DESIGN.md` e uso de assets PNG de referência.
- Novos fluxos implementados no frontend:
  - landing/home (`src/pages/Home.tsx`)
  - busca com lista + mapa (`src/pages/SearchPage.tsx`, `src/components/InstructorMap.tsx`, `src/components/InstructorCard.tsx`)
  - detalhes de reserva e seleção de slots (`src/pages/LessonDetails.tsx`, `src/components/SlotPicker.tsx`)
  - acompanhamento de agendamentos (`src/pages/MyLessons.tsx`, `src/components/BookingStatusBadge.tsx`, `src/components/BookingStatusTimeline.tsx`)
- Camada de tipos e serviços para US2 introduzida:
  - `src/types/instructor.ts`, `src/types/booking.ts`
  - `src/services/instructorSearch.ts`, `src/services/mockData.ts`
  - `src/features/bookings/bookingRules.ts`
- Testes de frontend e cobertura adicionados com Vitest + Testing Library:
  - `src/test/setup.ts`, `src/test/renderWithProviders.tsx`, `vitest.config.ts`
  - casos cobrindo regras de booking, componentes de status/slots e páginas de login/detalhes de aula.
- Validação executada com sucesso no frontend:
  - `npm run typecheck`
  - `npm run lint`
  - `npm run test`
  - `npm run test:coverage` (linhas/statements acima de 90%, branches acima de 77%)
  - `npm run build`

### Iteração 5

- Infraestrutura de desenvolvimento atualizada para reset determinístico do SQLite em startup:
  - `linkauto-backend/app/core/dev_db.py`
  - `linkauto-backend/app/main.py`
  - `linkauto-backend/app/core/config.py`
  - `linkauto-backend/.env.example`
- Backend passou a expor CORS configurável para frontend local (`CORS_ORIGINS`) com credenciais.
- Base de automação e2e adicionada no frontend com Playwright:
  - `linkauto-frontend/playwright.config.ts`
  - `linkauto-frontend/tests/e2e/student-booking-smoke.spec.ts`
  - scripts npm `e2e`, `e2e:headed`, `e2e:install` em `linkauto-frontend/package.json`
- Documentação de execução atualizada para fluxo manual + automatizado de e2e:
  - `README.md`
  - `docs/README.en.md`
  - `specs/001-user-booking-domains/quickstart.md`
