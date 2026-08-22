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
| Phase 6 - Polish | Concluída | Polimento e hardening completos, 13 itens de segurança e qualidade validados com 112 testes verdes e Ruff 100% |
| Phase 7 - Frontend Integration | Concluída | Integração completa com API real do backend, 100% livre de mocks de produção, typecheck TS limpo com exactOptionalPropertyTypes e 89 testes verdes do Vitest |

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

### Iteração 10 (Fase 6 - Hardening de Logging e Teste E2E de Integração Feliz)

- **Hardening de Segurança e Traceabilidade (T053):**
  - Implementado mecanismo assíncrono `correlation_id_ctx` usando `contextvars` (`app/core/logging.py`) para rastrear requisições sem vazamento de contexto.
  - Desenvolvido `CorrelationIDMiddleware` registrando o cabeçalho `X-Correlation-ID` em todas as respostas de API para rastreabilidade externa (OWASP A09).
  - Configurado o logger raiz e handlers do Uvicorn com `CorrelationIDFilter` para injetar automaticamente o Trace ID nos logs estruturados.
- **Teste E2E de Integração (T052):**
  - Desenvolvido o teste `tests/integration/test_e2e_happy_path.py` simulando com sucesso toda a jornada de ponta a ponta (cadastro e login de aluno/instrutor ➔ aprovação do instrutor pelo admin ➔ agendamento atômico e confirmação ➔ conciliação cron de conclusão ➔ chat de mensagens ➔ avaliações mútuas e recálculo da média).
- **Garantia de Qualidade e Testes:**
  - Validados todos os **95 testes verdes** e linter Ruff 100% limpo.

### Iteração 11 (Fase 6 - Polimento & Hardening Completo do Backend)

- **Hardening de Segurança e Resiliência (TDD):**
  - **D01 (Bloqueio de ADMIN público):** Adicionado validador no `RegisterRequest` e validação no `AuthService` impedindo registro público de admins, com testes unitários/integração.
  - **D03 (Mass Assignment no Profile PATCH):** Blindado o schema `UserMePatchRequest` encapsulando schemas aninhados e fechados (`StudentProfilePatch`, `InstructorProfilePatch`) usando `extra="forbid"`, ocultando `detran_status`, `rating_avg` e `rating_count`.
  - **D04 (Security Headers Middleware):** Middleware customizado injetando `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` e `Cache-Control` nas respostas de API.
  - **D05 (Configuração Segura Fail-Fast):** Implementado `@model_validator` na classe `Settings` para abortar a inicialização do app se senhas padrões ou resets automáticos forem usados em produção, emitindo warnings em caso de localhost no CORS.
  - **D06 (Magic Bytes nos Uploads):** Validador por assinaturas hexadecimais no `InstructorDocumentService` verificando os primeiros bytes de PDFs, JPEGs e PNGs para evitar spoofing de MIME.
  - **D11 (Resiliência do NotificationService):** Tratamento de falhas de rede no gateway de email com isolamento completo e logging `WARNING`, impedindo interrupção das transações principais de negócio.
  - **D08 (SQL Hardening no BookingLockStore):** Removido `table_name` dinâmico do construtor, fixando a constante estática `_TABLE_NAME = "slots"` nas queries SQL.
  - **D12 (Otimização de Queries N+1):** Otimizado `cancel_booking()` no `BookingService` para usar cláusula `IN` batch, reduzindo as consultas de O(n) para O(1).
  - **D13 (Resiliência per-item no Scheduler):** Adicionado try/except individual no lote do scheduler para garantir o processamento contínuo de itens saudáveis mesmo sob falhas isoladas, retornando contadores estruturados.
  - **D07 (Logging Estruturado de Eventos de Segurança):** Implementado mascaramento de tokens e logs de auditoria detalhados no `/login`, aprovações e rejeições administrativas.
  - **D09 (Rate Limiting com SlowAPI):** Implementado rate-limiting em memória por IP com SlowAPI e SlowAPIMiddleware, limitando login (10/min), registro (5/min), refresh (20/min) e reset (3/min), com handler formatado de erro `429 Too Many Requests` (`RATE_LIMIT_EXCEEDED`).
  - **D10 (Testes de Abuso & Cobertura):** Desenvolvido `tests/security/test_abuse_scenarios.py` cobrindo 100% das regras e rate limits, com fixture global autouse em `tests/conftest.py` para resetar o estado do limiter garantindo estrito isolamento.
- **Garantia de Qualidade e Testes:**
  - Rodada a suíte completa de testes: todos os **112 testes verdes** e Uruff 100% em conformidade com PEP 8.

### Iteração 12 (Fase 7 - Integração de Frontend Completa e Verde)

- **Integração de Ponta a Ponta com a API do Backend:**
  - Conectadas todas as páginas da aplicação (`SearchPage`, `MyLessons`, `LessonDetails`, `Profile`, `Home`) à API de produção do backend (FastAPI + SQLite3).
  - Removido o uso de mocks de dados em produção, mapeando o arquivo `mockData.ts` exclusivamente em `src/test/fixtures/` para a suíte de testes.
  - Implementada a service layer no frontend (`instructorService`, `slotService`, `bookingService`, `profileService`, `messageService`, `reviewService`) com mapeadores (mappers) de objetos robustos convertendo tipos `snake_case` do backend FastAPI em `camelCase` e tratando potenciais valores nulos para strings vazias para melhor UX e controle no React.
  - Adicionado suporte a geolocalização nativa via GPS com fallback resiliente para dropdown manual de cidades contendo coordenadas geográficas centrais reais da microrregião de Mogi Mirim.
  - Desenvolvido interceptor de refresh de token silencioso em `src/services/httpClient.ts` in case of `401 Unauthorized` errors using HTTPOnly cookie, connected to `SessionProvider` in `sessionStore.tsx`.
  - Adicionado script de seed automático de dados de alta fidelidade no startup de desenvolvimento do backend (`app/core/dev_db.py`) semeando admin, aluno de teste, 3 instrutores credenciados com fotos reais e histórico rico de slots/aulas avaliadas.
- **Resiliência e Correção Estrita do TypeScript:**
  - Garantida total conformidade com as regras estritas do TypeScript no `tsconfig.json` (`exactOptionalPropertyTypes: true` e `noUncheckedIndexedAccess: true`), tipando explicitamente as propriedades opcionais como `| undefined` nas interfaces e estados do Profile, SearchPage e LessonDetails.
  - Implementado mecanismo de cleanup com flag `active` no `useEffect` de carregamento de slots de `LessonDetails.tsx` para evitar vazamentos de estado em testes do Vitest que causavam o erro de ambiente desmontado `ReferenceError: window is not defined`.
- **Garantia de Qualidade e Suíte de Testes:**
  - Ajustadas as expectativas de testes unitários em `ScaffoldPages.test.tsx` e `LessonDetails.test.tsx` para se manterem fiéis às novas assinaturas e layouts de UI baseados em perfis.
  - Rodada a suíte completa de testes de frontend: todos os **89 testes do Vitest passando com 100% de sucesso**.
  - Executado o `npm run typecheck` completando com **sucesso absoluto e zero erros**.

### Iteração 13 (Fase 7 - Correção de Bug CORS/Erro 500 no Cancelamento de Reservas)

- **Correção de Timezone Aware vs Naive no Backend (Erro 500 / CORS):**
  - Identificado e resolvido o bug crítico de `TypeError: can't subtract offset-naive and offset-aware datetimes` no endpoint `PATCH /api/v1/bookings/{id}/cancel` em `app/services/booking_service.py` (L179).
  - O SQLite no Python retorna datas naive datetime sem fuso horário, enquanto `datetime.now(timezone.utc)` gera uma data timezone-aware, provocando um erro interno 500 que ocultava o cabeçalho de CORS e impedia o cancelamento pelo aluno.
  - Implementado fallback resiliente em `BookingService.cancel_booking()` garantindo que o `starts_at` do slot seja convertido em timezone-aware UTC se for naive, assegurando a compatibilidade perfeita do SQLite com PostgreSQL em produção.
- **Garantia de Qualidade e Testes:**
  - Rodada a suíte completa de testes unitários e de integração do backend: todos os **112 testes do pytest verdes**.

### Iteração 14 (Modernização de Infraestrutura Docker & Documentação Completa)

- **Empacotamento com Dockerfiles Multi-Stage:**
  - Criado `linkauto-backend/Dockerfile` e `linkauto-backend/.dockerignore` com estágios `base`, `development` (hot-reload `uvicorn --reload`) e `production` (usuário não-root e instalação enxuta).
  - Criado `linkauto-frontend/Dockerfile` e `linkauto-frontend/.dockerignore` com estágios `base`, `development` (Vite dev server), `build` (`npm run build`) e `production` (servidor estático Nginx Alpine).
- **Orquestração com Docker Compose:**
  - Refatorado `infra/docker-compose.yml` utilizando os Dockerfiles multi-stage como alvo de desenvolvimento.
  - Adicionados healthchecks automatizados na API backend (`/health`) e isolamento de volumes para `node_modules` no frontend e `.venv` no backend.
  - Mapeado serviço opcional `postgres` com PostGIS sob o perfil `--profile postgres` para paridade com produção.
- **Documentação de Infraestrutura & Guia de Comandos:**
  - Criado o manual completo `infra/README.md` com tabela de comandos essenciais, execução de testes dentro de containers, troubleshooting e guia passo a passo para usuários não-técnicos via Docker Desktop.
  - Atualizado o `README.md` raiz com atalhos de inicialização e links diretos.
- **Garantia de Qualidade e Testes:**
  - Sintaxe de compose validada com sucesso (`docker compose -f infra/docker-compose.yml config`).
  - Suítes de testes 100% validadas: **112 testes pytest verdes** no backend e **94 testes vitest verdes + typecheck TS limpo** no frontend.

### Iteração 15 (Endpoints Full-Stack: Filtros Avançados de Busca & Dashboards de Estatísticas)

- **Filtros Avançados e Ordenação de Instrutores (Slice 1):**
  - Implementada filtragem por `specialties` (case-insensitive com correspondência de termos) e ordenação `sort_by` (`rating`, `price_asc`, `price_desc`, `distance`) no serviço `InstructorSearchService` e endpoint `GET /api/v1/instructors/search`.
  - Integrado no frontend em `instructorService.ts` e `SearchPage.tsx` com novo seletor de ordenação Chakra UI v3.
  - Testes: Adicionados `test_instructor_search_advanced.py` (unit) e `test_instructor_search_advanced_contract.py` (contract).
- **Dashboard de Estatísticas Administrativas (Slice 2):**
  - Implementado endpoint `GET /api/v1/admin/stats` restrito a administradores (`ADMIN`) com `AdminStatsService` agregando `total_instructors`, `pending_instructors`, `approved_instructors`, `rejected_instructors`, `total_students` e `total_bookings`.
  - Integrado no frontend em `InstructorDashboard.tsx` e `AdminInstructorDashboardRoute` em `router.tsx` exibindo cards com dados em tempo real.
  - Testes: Adicionados `test_admin_stats_service.py` (unit) e `test_admin_stats_contract.py` (contract).
- **Dashboard de Estatísticas do Instrutor (Slice 3):**
  - Implementado endpoint `GET /api/v1/instructor/stats` restrito a instrutores (`INSTRUTOR`) com `InstructorStatsService` agregando `total_lessons`, `total_hours`, `unique_students` e `pending_bookings`.
  - Integrado no frontend em `InstructorDashboard.tsx` e `InstructorDashboardRoute` em `router.tsx` exibindo métricas ao vivo do instrutor.
  - Testes: Adicionados `test_instructor_stats_service.py` (unit) e `test_instructor_stats_contract.py` (contract).
- **Garantia de Qualidade e Suítes de Testes:**
  - Backend: **128 testes pytest verdes (100% de aprovação)** e **Ruff lint 100% limpo**.
  - Frontend: **94 testes Vitest verdes (100% de aprovação)** e **TypeScript `npm run typecheck` 100% limpo**.

### Iteração 16 (Perfis Públicos & Roteamento Dinâmico com Blindagem LGPD)

- **Endpoints Públicos e Blindagem de Dados LGPD no Backend (Slice 1):**
  - Implementados endpoints REST anônimos `GET /api/v1/instructors/{id}/public` e `GET /api/v1/students/{id}/public` (`app/api/v1/public_profiles.py`).
  - Desenvolvido `PublicProfileService` (`app/services/public_profile_service.py`) com sanitização estrita de PII (ocultação total de `email`, `phone`, `password_hash`, `cpf`, dados bancários e status de penalidade).
  - Aplicada regra de visibilidade **RN01**: instrutores pendentes ou inativos retornam estritamente `404 Not Found`.
  - Agregação de avaliações públicas mútuas (`Review`) com resolução de autor e contagem de aulas realizadas (`Booking`).
  - Testes: Adicionados `test_public_profile_service.py` (unit) e `test_public_profile_contract.py` (contract).
- **Páginas de Perfil Público e Roteamento no Frontend (Slice 2):**
  - Criadas as páginas públicas `InstructorPublicProfilePage.tsx` e `StudentPublicProfilePage.tsx` com Chakra UI v3, badges semânticos, timeline de feedback e seletor de horários interativo `SlotPicker`.
  - Criados métodos `fetchPublicInstructorProfile` e `fetchPublicStudentProfile` em `profileService.ts`.
  - Registradas as rotas dinâmicas `/instructors/:id` e `/students/:id` no `router.tsx`.
- **Integração de Navegação e Desacoplamento da Rota `/profile` (Slice 3):**
  - Atualizado `InstructorCard.tsx` e `SearchPage.tsx` para direcionar o botão "Ver perfil" para `/instructors/${id}`.
  - Atualizado `Profile.tsx` (configurações privadas) adicionando atalho "Visualizar meu perfil público".
  - Conectados links navegáveis em `LessonDetails.tsx` e `MyLessons.tsx` para os perfis públicos de instrutores e alunos.
- **Garantia de Qualidade e Suítes de Testes:**
  - Backend: **136 testes pytest verdes (100% de aprovação)** e **Ruff lint 100% limpo**.
  - Frontend: **97 testes Vitest verdes (100% de aprovação)** e **TypeScript `npm run typecheck` 100% limpo**.

### Iteração 17 (Ocultação de UUIDs Internos via Slugs Públicos & Remoção de Slots de Perfis Públicos)

- **Slugs Públicos e Ocultação Total de UUIDs no Backend (Slice 1):**
  - Criado o gerador de slugs seguros e amigáveis `app/core/slug.py` com normalização ASCII e sufixo de entropia único (ex: `carlos-silva-mogi-mirim-8f2a`).
  - Adicionada coluna indexada e única `slug` em `InstructorProfile` e `StudentProfile` (`app/models/user.py`).
  - Criada migration Alembic `0004_profile_slugs.py` para as tabelas `instructor_profiles` e `student_profiles`.
  - Atualizado `PublicProfileService` para buscar por `slug` e retornar os slugs públicos tanto para o perfil quanto para as referências de autores de reviews, garantindo que nenhum UUID interno seja exposto em contratos públicos.
  - Atualizado endpoint `GET /api/v1/instructors/search` para expor o `slug` público.
  - Testes: Atualizados `test_public_profile_service.py` e `test_public_profile_contract.py` com checagem estrita de não-vazamento de UUIDs internos.
- **Remoção de Slots & Roteamento por Slugs no Frontend (Slice 2):**
  - Removido `SlotPicker` e a busca de slots da página `InstructorPublicProfilePage.tsx`, eliminando exposição de horários sem autenticação.
  - Implementado botão principal *"Agendar Aula com este Instrutor"* com redirecionamento contextual para `/bookings/new` ou `/login`.
  - Atualizados `InstructorCard.tsx`, `SearchPage.tsx`, `Profile.tsx`, `MyLessons.tsx` e `LessonDetails.tsx` para utilizarem estritamente os slugs públicos nas rotas `/instructors/:slug` e `/students/:slug`.
  - Atualizada suíte de testes de componentes `PublicProfiles.test.tsx`.
- **Garantia de Qualidade e Suítes de Testes:**
  - Backend: **136 testes pytest verdes (100% de aprovação)** e **Ruff lint 100% limpo**.
  - Frontend: **97 testes Vitest verdes (100% de aprovação)** e **TypeScript `npm run typecheck` 100% limpo**.



