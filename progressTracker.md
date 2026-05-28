# progressTracker

## Contexto

Rastreamento incremental da implementação da feature `001-user-booking-domains`.

## Status por fase

| Fase | Estado | Observação |
| ------ | -------- | ------------ |
| Phase 1 - Setup | Concluída | T001-T006 finalizadas |
| Phase 2 - Foundational | Concluída | T007-T017 finalizadas e validadas |
| Phase 3 - US1 | Concluída | T018-T029 + T056/T057 finalizadas |
| Phase 4 - US2 | Concluída | Backend e Frontend US2 completos, com todos os testes validados (67 testes verdes) |
| Phase 5 - US3 | Concluída | Mensagens, avaliações, lembrete 24h e 8 tipos de notificações de e-mail (94 testes verdes) |
| Phase 6 - Polish | Em andamento | Polimento e validação de regressão finalizada no backend |

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

### Iteração 6 (US2 Backend - Fundação, Modelos e Serviços de Booking)

- Criada branch de isolamento de desenvolvimento `feature/us2-booking-scheduling`.
- Implementada infraestrutura de banco de dados e testes integrados para US2:
  - Definida dependência FastAPI `get_db()` usando sessões síncronas do SQLAlchemy 2.0 (`app/core/database.py`).
  - Desenvolvidas fixtures transacionais isoladas (`tests/conftest_db.py`, `tests/conftest.py`) com rollback automático para testes com banco SQLite em memória.
- Implementada modelagem de dados sintonizada com PostgreSQL / SQLite com integridade referencial:
  - Novos modelos ORM mapeados: `Slot` (status DISPONIVEL/RESERVADO/BLOQUEADO), `Booking` (status PENDENTE/CONFIRMADA/REALIZADA/CANCELADA), tabela de associação única `BookingSlot` e `StudentPenalty` (`app/models/slot.py`, `app/models/booking.py`).
  - Adicionada migration Alembic `0002_booking_constraints.py` para as quatro novas tabelas, com índices compostos otimizados para busca e performance.
- Implementados schemas Pydantic blindados contra Mass Assignment (Task 4) com validações robustas:
  - Validação estrita de duração de **exatamente 1 hora** para slots individuais (`app/schemas/slot.py`).
  - Validação de limite mínimo de **2 slots consecutivos** para solicitações de reserva (`app/schemas/booking.py`).
  - Schemas administrativos estritos blindando transições de status apenas para estados terminais.
- Implementados serviços de negócio com as regras especificadas e validações em profundidade (Defense in Depth):
  - **`SlotService`:** Garante criação, listagem e exclusão segura de slots com checagem de sobreposição por instrutor.
  - **`PenaltyService`:** Valida bloqueios ativos e aplica suspensão de 7 dias conforme a regra **RN04**.
  - **`BookingService`:** Gerencia o ciclo de vida das reservas. Valida restrições geográficas futuras, consecutividade de slots, integridade de instrutor, bloqueio preventivo de alunos penalizados, transições de estado robustas e aplicação de penalidade caso o cancelamento ocorra a menos de 24 horas da aula (**RN04**).
- Cobertura de testes unitários expandida em TDD (RED-GREEN): 22 novos testes passando com sucesso, totalizando 45 testes unitários e de integração verdes e validados.

### Iteração 7 (US2 Backend Completo e Integração de Testes)

- Concluída a implementação integral do backend para a US2 (Booking & Scheduling):
  - Endpoints REST `/slots` e `/bookings` fully functional (`app/api/v1/slots.py`, `app/api/v1/bookings.py`).
  - Geosearch de instrutores ativos e aprovados utilizando fórmula de Haversine (`app/api/v1/instructor_search.py`, `app/services/instructor_search_service.py`).
  - Tarefas de automação (timeout 24h e conclusão automática após +2h) com endpoints administrativos expostos (`app/jobs/booking_jobs.py`).
  - Handler global de erros traduzindo `IntegrityError` do SQLAlchemy em resposta estruturada de `409 Conflict`.
- Execução e validação da suíte completa de testes:
  - 67 testes passando com 100% de sucesso (unitários, integração, contratos e regressão).
  - Cobertura total blindada contra regressão de agendamentos.

### Iteração 8 (US3 Backend - Chat de Mensagens, Avaliações Mútuas e E-mails)

- Concluída a implementação integral do backend para a US3 (Messages, Reviews & Notifications):
  - **Modelagem ORM & Migrações:** Criadas as tabelas `booking_messages` e `reviews` com restrições exclusivas (uma avaliação por sentido por agendamento) e índices compostos otimizados.
  - **UTC Datetime Serialization:** Serialização centralizada com Pydantic para garantir que todos os datetimes terminem estritamente com o sufixo ISO 8601 `Z` (UTC).
  - **Serviços de Negócio:**
    - `BookingMessageService` gerenciando envio e listagem cronológica do chat, disparando e-mail de notificação.
    - `ReviewService` tratando avaliações mútuas apenas para status `REALIZADA`, atualizando atomicamente média/contador do instrutor no `InstructorProfile`.
  - **Catálogo de Notificações por E-mail:** Implementação de 8 tipos de e-mails em todo o ciclo de vida (pendente, confirmação, cancelamentos, nova mensagem, avaliação, lembrete).
  - **Lesson Reminder Job:** Job/endpoint cron `/jobs/booking-reminder` que varre agendamentos confirmados e envia avisos 24 horas antes do início da aula.
  - **API Routers protegidos:** Endpoints `/bookings/{id}/messages` e `/bookings/{id}/reviews` com RBAC rigoroso impedindo acesso por terceiros (retornando 403/404).

### Iteração 9 (Polimento, Ruff e Garantia de Qualidade)

- Rodada a suíte completa de testes unitários, contratos e fluxos integrados: **todos os 94 testes passando com 100% de sucesso**.
- Validada a conformidade de linter com Ruff (`ruff check .`), limpando todas as importações e dependências não utilizadas.
- Feito o hardening de segurança conforme as diretrizes do `docs/SECURITY_TECHNIQUES.md`.

