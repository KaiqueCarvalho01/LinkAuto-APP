# Progress Tracker Frontend - LinkAuto

## Data

- 2026-04-18

## Diretrizes operacionais ativas

- Escopo por iteracao: no maximo 4 tasks ou 1 feature delimitada de user story.
- Qualidade XP obrigatoria: ciclo red-green por task (teste falhando antes da implementacao final).
- Cobertura minima por fatia alterada: 80%.
- Rastreabilidade obrigatoria em markdown: registrar o que foi feito, onde foi feito (arquivos) e como foi validado (comandos e resultado).
- Atualizacao obrigatoria ao final de cada iteracao neste arquivo (`progressTracker-frontend.md`).
- Mock-first permitido e recomendado quando endpoint backend nao estiver contratado/disponivel.
- Necessidade de novo endpoint: registrar justificativa antes de implementacao em `specs/002-frontend-iterative-spec/endpoint-requests.md`.

## Iteracao 1 - Base Chakra UI + TypeScript Strict

### Objetivo (Iteracao 1)

Consolidar o frontend em React 19 com TypeScript strict, Chakra UI como fundacao visual e manter o fluxo US1 funcional (login, perfil e painel admin), alinhado aos endpoints backend existentes.

### Entregas concluidas (Iteracao 1)

- Migracao do frontend para TypeScript strict:
  - `linkauto-frontend/tsconfig.json`
  - `linkauto-frontend/tsconfig.app.json`
  - `linkauto-frontend/tsconfig.node.json`
- Vite migrado para TypeScript:
  - `linkauto-frontend/vite.config.ts`
- Entry-point em TSX com `ChakraProvider`:
  - `linkauto-frontend/src/main.tsx`
- Tema Chakra baseado na identidade LinkAuto (azul + verde):
  - `linkauto-frontend/src/theme/system.ts`
- Tipagem forte para API e sessao:
  - `linkauto-frontend/src/types/api.ts`
  - `linkauto-frontend/src/types/session.ts`
  - `linkauto-frontend/src/services/httpClient.ts`
  - `linkauto-frontend/src/services/config.ts`
  - `linkauto-frontend/src/state/sessionStore.tsx`
- Router tipado e protegido para US1:
  - `linkauto-frontend/src/app/router.tsx`
- Redesign das telas ativas com Chakra UI:
  - `linkauto-frontend/src/pages/Login.tsx`
  - `linkauto-frontend/src/pages/Profile.tsx`
  - `linkauto-frontend/src/pages/InstructorDashboard.tsx`
  - `linkauto-frontend/src/components/BrandLockup.tsx`
- Limpeza de legado JSX para evitar colisao de resolucao de modulo e garantir base TS no `src/`.

### Validacao executada (Iteracao 1)

- `cd linkauto-frontend && npm run typecheck` ✅
- `cd linkauto-frontend && npm run lint` ✅
- `cd linkauto-frontend && npm run build` ✅

### Riscos / observacoes (Iteracao 1)

- Build emite alerta de chunk > 500 kB. Nao bloqueante nesta iteracao.
- Fluxos US2/US3 ainda dependem de endpoints backend nao finalizados (slots/bookings/messages/reviews).

## Proxima iteracao sugerida (Iteracao 2)

- Implementar camada tipada para US2:
  - `instructors/search`
  - `bookings` (create/list/detail/confirm/cancel)
- Criar telas Chakra para busca, agenda e detalhes de reserva com estados de loading/erro.
- Introduzir code splitting por rota para reduzir bundle inicial.

## Iteracao 2 - US2 frontend preview + cobertura automatizada

### Objetivo (Iteracao 3)

Aplicar o guia visual de `docs/DESIGN.md` e assets PNG no frontend, expandir a experiencia do aluno para os fluxos US2 (busca, mapa, selecao de slots e acompanhamento de agendamentos) e elevar confianca com testes automatizados e cobertura minima controlada.

### Entregas concluidas (Iteracao 3)

- Identidade visual e assets alinhados ao DESIGN:
  - `linkauto-frontend/src/theme/system.ts`
  - `linkauto-frontend/src/index.css`
  - `linkauto-frontend/public/design/*`
  - `linkauto-frontend/public/brand/*`
- Novos tipos e servicos para busca/agendamento:
  - `linkauto-frontend/src/types/instructor.ts`
  - `linkauto-frontend/src/types/booking.ts`
  - `linkauto-frontend/src/services/instructorSearch.ts`
  - `linkauto-frontend/src/services/mockData.ts`
  - `linkauto-frontend/src/features/bookings/bookingRules.ts`
- Novos componentes de fluxo US2:
  - `linkauto-frontend/src/components/InstructorCard.tsx`
  - `linkauto-frontend/src/components/InstructorMap.tsx`
  - `linkauto-frontend/src/components/SlotPicker.tsx`
  - `linkauto-frontend/src/components/BookingStatusBadge.tsx`
  - `linkauto-frontend/src/components/BookingStatusTimeline.tsx`
  - `linkauto-frontend/src/components/RatingStars.tsx`
- Novas paginas e navegacao:
  - `linkauto-frontend/src/pages/Home.tsx`
  - `linkauto-frontend/src/pages/SearchPage.tsx`
  - `linkauto-frontend/src/pages/LessonDetails.tsx`
  - `linkauto-frontend/src/pages/MyLessons.tsx`
  - `linkauto-frontend/src/app/router.tsx`
- Base de testes frontend com Vitest + Testing Library:
  - `linkauto-frontend/vitest.config.ts`
  - `linkauto-frontend/src/test/setup.ts`
  - `linkauto-frontend/src/test/renderWithProviders.tsx`
  - `linkauto-frontend/src/features/bookings/bookingRules.test.ts`
  - `linkauto-frontend/src/components/BookingStatusBadge.test.tsx`
  - `linkauto-frontend/src/components/SlotPicker.test.tsx`
  - `linkauto-frontend/src/pages/Login.test.tsx`
  - `linkauto-frontend/src/pages/LessonDetails.test.tsx`

### Validacao executada

- `cd linkauto-frontend && npm run typecheck` ✅
- `cd linkauto-frontend && npm run lint` ✅
- `cd linkauto-frontend && npm run test` ✅
- `cd linkauto-frontend && npm run test:coverage` ✅
  - Statements: 91.47%
  - Branches: 77.27%
  - Functions: 94.73%
  - Lines: 91.47%
- `cd linkauto-frontend && npm run build` ✅

### Riscos / observacoes

- Fluxo US2 no frontend esta funcional em modo API-first com fallback de mock para endpoints ainda nao consolidados no backend.
- Build ainda sinaliza alerta de chunk > 500 kB (nao bloqueante).
- Foi identificado aviso de vulnerabilidade em auditoria npm durante instalacao (nao bloqueou build/testes).

## Proxima iteracao sugerida (Iteracao 3)

- Conectar completamente os fluxos US2 aos endpoints reais de backend e remover fallback mock onde nao for mais necessario.
- Introduzir lazy loading por rota para reduzir bundle inicial (especialmente telas com mapa).
- Expandir testes para cenarios de erro/rede, guardas de rota e estados de bloqueio de reserva.

## Iteracao 3 - Bootstrap de e2e com Playwright

### Objetivo (Iteracao 4)

Criar uma trilha de teste e2e reproduzivel para validar rapidamente o fluxo principal de aluno (login, busca e solicitacao de agendamento), com suporte a execucao local automatizada e execucao manual assistida.

### Entregas concluidas (Iteracao 4)

- Configuracao base do Playwright para o frontend:
  - `linkauto-frontend/playwright.config.ts`
- Smoke e2e implementado para fluxo aluno:
  - `linkauto-frontend/tests/e2e/student-booking-smoke.spec.ts`
- Scripts npm adicionados:
  - `e2e`
  - `e2e:headed`
  - `e2e:install`
  - arquivo: `linkauto-frontend/package.json`

### Validacao executada (Iteracao 4)

- `cd linkauto-frontend && npm run e2e:install` ✅
- `cd linkauto-frontend && npm run e2e` ✅

### Riscos / observacoes (Iteracao 4)

- O smoke e2e assume backend ativo em `http://127.0.0.1:8000` para registro/login via API.
- Sem backend ativo, o teste falha antes de validar o fluxo de UI.

## Iteracao 4 - Polimento visual, contraste e dark mode

### Objetivo

Eliminar pontos de baixo contraste em todas as telas ativas, padronizar o uso de tokens semanticos Chakra e disponibilizar troca de tema claro/escuro persistente para o usuario, mantendo a identidade visual LinkAuto.

### Entregas concluidas

- Dark mode global com persistencia local e toggle fixo em tela:
  - `linkauto-frontend/src/app/router.tsx`
- Expansao de tokens semanticos para estados de feedback (warning/success/danger) e texto inverso:
  - `linkauto-frontend/src/theme/system.ts`
- Migracao de cores hardcoded para tokens semanticos nas paginas:
  - `linkauto-frontend/src/pages/Home.tsx`
  - `linkauto-frontend/src/pages/SearchPage.tsx`
  - `linkauto-frontend/src/pages/Login.tsx`
  - `linkauto-frontend/src/pages/LessonDetails.tsx`
  - `linkauto-frontend/src/pages/MyLessons.tsx`
  - `linkauto-frontend/src/pages/Profile.tsx`
  - `linkauto-frontend/src/pages/InstructorDashboard.tsx`
- Migracao de cores hardcoded para tokens semanticos nos componentes compartilhados:
  - `linkauto-frontend/src/components/InstructorCard.tsx`
  - `linkauto-frontend/src/components/InstructorMap.tsx`
  - `linkauto-frontend/src/components/SlotPicker.tsx`
  - `linkauto-frontend/src/components/BookingStatusBadge.tsx`
  - `linkauto-frontend/src/components/BookingStatusTimeline.tsx`
  - `linkauto-frontend/src/components/RatingStars.tsx`
  - `linkauto-frontend/src/components/BrandLockup.tsx`
- Ajuste da configuracao de testes para separar unitarios (Vitest) de e2e (Playwright):
  - `linkauto-frontend/vitest.config.ts`

### Validacao executada (Iteracao 4)

- `cd linkauto-frontend && npm run typecheck` ✅
- `cd linkauto-frontend && npm run lint` ✅
- `cd linkauto-frontend && npm run test` ✅
- `cd linkauto-frontend && npm run build` ✅
- `cd linkauto-frontend && npm run e2e -- --project=chromium` ✅

### Riscos / observacoes (Iteracao 4)

- O bundle principal permanece acima de 500kB apos minificacao; continua nao bloqueante, mas recomenda-se code splitting por rota (especialmente mapa e dashboard).
- O popup do Leaflet permanece com cores explicitas em tons claros para preservar legibilidade no container visual branco do proprio Leaflet.
- O arquivo `docs/DESIGN.md` possui backlog de padronizacao de Markdown (MD013/MD060 e afins) em secoes historicas; a iteracao atual atualizou conteudo funcional sem normalizacao completa de estilo para evitar refatoracao documental massiva.

## Iteracao 5 - Frontend governance baseline (spec 002)

### Entregas concluidas (Iteracao 5)

- Templates markdown de governanca para ciclo, red-green, coverage gate e integration boundary.
- Modulo de validacao de politica de fatia (maximo 4 tasks ou 1 user story feature).
- Modulo de validacao de ordem de scaffold de rota antes de UI final.
- CLI de validacao de governanca e script npm associado.

### Onde foi entregue (Iteracao 5)

- `specs/002-frontend-iterative-spec/checklists/iteration-slice-template.md`
- `specs/002-frontend-iterative-spec/checklists/red-green-evidence-template.md`
- `specs/002-frontend-iterative-spec/checklists/coverage-gate-template.md`
- `specs/002-frontend-iterative-spec/checklists/integration-boundary-template.md`
- `specs/002-frontend-iterative-spec/checklists/v1-scope-guardrails.md`
- `specs/002-frontend-iterative-spec/iterations/README.md`
- `specs/002-frontend-iterative-spec/iterations/iteration-001.md`
- `linkauto-frontend/src/features/iteration-governance/logLoader.ts`
- `linkauto-frontend/src/features/iteration-governance/logLoader.test.ts`
- `linkauto-frontend/src/features/iteration-governance/slicePolicy.ts`
- `linkauto-frontend/src/features/iteration-governance/slicePolicy.test.ts`
- `linkauto-frontend/src/features/iteration-governance/routePlanningRule.ts`
- `linkauto-frontend/src/features/iteration-governance/routePlanningRule.test.ts`
- `linkauto-frontend/src/features/iteration-governance/index.ts`
- `linkauto-frontend/scripts/validate-governance.mjs`
- `linkauto-frontend/package.json`

### Validacao executada (Iteracao 5)

- `cd linkauto-frontend && npm run test -- src/features/iteration-governance/logLoader.test.ts` ✅
- `cd linkauto-frontend && npm run test -- src/features/iteration-governance/slicePolicy.test.ts src/features/iteration-governance/routePlanningRule.test.ts` ✅

### Riscos / observacoes (Iteracao 5)

- Validadores de quality gate completo e endpoint-request prerequisito serao implementados nos proximos blocos (US2/US3).

## Iteracao 6 - US2 quality gates (spec 002)

### Entregas concluidas (Iteracao 6)

- Validadores de evidência red-green por task.
- Validador de threshold de cobertura no escopo alterado.
- Regras da CLI de governança expandidas para exigir campos red-green e métricas de cobertura.
- Registro do quality gate no ciclo 001 atualizado com métricas reais de cobertura.

### Onde foi entregue (Iteracao 6)

- specs/002-frontend-iterative-spec/tasks.md
- specs/002-frontend-iterative-spec/iterations/iteration-001.md
- linkauto-frontend/src/features/iteration-governance/qualityGate.ts
- linkauto-frontend/src/features/iteration-governance/qualityGate.test.ts
- linkauto-frontend/src/features/iteration-governance/coveragePolicy.ts
- linkauto-frontend/src/features/iteration-governance/coveragePolicy.test.ts
- linkauto-frontend/src/features/iteration-governance/index.ts
- linkauto-frontend/scripts/validate-governance.mjs

### Validacao executada (Iteracao 6)

- `cd linkauto-frontend && npm run test -- src/features/iteration-governance/qualityGate.test.ts src/features/iteration-governance/coveragePolicy.test.ts` ✅
- `cd linkauto-frontend && npx vitest run src/features/iteration-governance/qualityGate.test.ts src/features/iteration-governance/coveragePolicy.test.ts --coverage --coverage.include='src/features/iteration-governance/qualityGate.ts' --coverage.include='src/features/iteration-governance/coveragePolicy.ts'` ✅
- `cd linkauto-frontend && npm run typecheck && npm run lint && npm run validate:governance` ✅

### Riscos / observacoes (Iteracao 6)

- Bloco US3 (integration boundary resolver + endpoint request policy) permanece pendente para completar governança de integração com backend.

## Iteracao 7 - US3 integration boundaries (spec 002)

### Entregas concluidas (Iteracao 7)

- Testes TDD para lógica de `integrationBoundary` e `endpointRequestPolicy`.
- Resolutores e validadores implementados para fallback mock-first e prerrequisitos de requests de endpoints.
- Documentação de contratos preenchida com mapeamento de capacidades (mock vs contratado).
- Exemplo de ciclo de vida de `endpoint-requests` criado em `endpoint-requests.md`.

### Onde foi entregue (Iteracao 7)

- `linkauto-frontend/src/features/iteration-governance/integrationBoundary.test.ts`
- `linkauto-frontend/src/features/iteration-governance/endpointRequestPolicy.test.ts`
- `linkauto-frontend/src/features/iteration-governance/integrationBoundary.ts`
- `linkauto-frontend/src/features/iteration-governance/endpointRequestPolicy.ts`
- `linkauto-frontend/src/features/iteration-governance/index.ts`
- `specs/002-frontend-iterative-spec/contracts/frontend-iteration-governance.md`
- `specs/002-frontend-iterative-spec/endpoint-requests.md`
- `specs/002-frontend-iterative-spec/tasks.md`

### Validacao executada (Iteracao 7)

- `cd linkauto-frontend && npm run test -- src/features/iteration-governance/integrationBoundary.test.ts src/features/iteration-governance/endpointRequestPolicy.test.ts` ✅
- `cd linkauto-frontend && npm run validate:governance` ✅

### Riscos / observacoes (Iteracao 7)

- O frontend está pronto com suas políticas de governança locais.

## Iteracao 8 - Polish final de Governança (spec 002)

### Entregas concluidas (Iteracao 8)

- Consolidação e validação full bundle da base de governança.
- `landpage_UX.md` documentado com as políticas cruzadas.
- Rastreamento geral consolidado.

### Onde foi entregue (Iteracao 8)

- `docs/designs/landpage_UX.md`
- `specs/002-frontend-iterative-spec/tasks.md`

### Validacao executada (Iteracao 8)

- `cd linkauto-frontend && npm run build` ✅
- `cd linkauto-frontend && npm run e2e -- --project=chromium` ✅

### Riscos / observacoes (Iteracao 8)

- Finalizadas todas as tasks de spec 002 com sucesso sem quebrar fluxo principal do estudante de marcação (comprovado no teste e2e).

## Iteracao 9 - Refactor Scaffold and Instructions (spec 002)

### Entregas concluidas (Iteracao 9)

- Refactored `copilot-instructions.md` with structured guidelines and project constraints.
- Refactored `FE-008` (Scaffold + Router) from Portuguese to English to comply with constitutional constraints.
- Updated all component names, internal text, file paths, and imports to English.
- Verified rendering tests for all scaffold pages.

### Onde foi entregue (Iteracao 9)

- `.github/copilot-instructions.md`
- `linkauto-frontend/src/app/router.tsx`
- `linkauto-frontend/src/pages/` (renamed and refactored files)
- `linkauto-frontend/src/pages/ScaffoldPages.test.tsx`

### Validacao executada (Iteracao 9)

- `cd linkauto-frontend && npm run test -- src/pages/ScaffoldPages.test.tsx` ✅
- `cd linkauto-frontend && npm run build` ✅

### Riscos / observacoes (Iteracao 9)

- Ensured all routes are working with English paths (e.g., `/register`, `/about`, `/students/how-it-works`).
- Next step: proceed to `FE-001` (Visitor Navbar) with high-quality design standards.

## Iteracao 10 - Visitor Navbar (FE-001)

### Entregas concluidas (Iteracao 10)

- Visitor Navbar component with dropdowns for Students and Instructors.
- Responsive design with a mobile-first approach.
- Scroll-triggered shadow and blur effect for a modern look.

### Onde foi entregue (Iteracao 10)

- `linkauto-frontend/src/components/Navbar.tsx`
- `linkauto-frontend/src/components/Navbar.test.tsx`

### Validacao executada (Iteracao 10)

- `npm run test -- src/components/Navbar.test.tsx` ✅

## Iteracao 11 - Authenticated Navbar (FE-002)

### Entregas concluidas (Iteracao 11)

- Authenticated Navbar with Notifications Popover and User Avatar.
- Functional Mobile Drawer for both visitor and authenticated states.
- Mock notification list for FE-002.

### Onde foi entregue (Iteracao 11)

- `linkauto-frontend/src/components/Navbar.tsx`
- `linkauto-frontend/src/components/Navbar.test.tsx`

### Validacao executada (Iteracao 11)

- cycle_id: iteration-004
- red_command: `npm run test -- src/components/Navbar.test.tsx` ✅
- green_command: `npm run test -- src/components/Navbar.test.tsx` ✅
- coverage_pct: 100% (Line), 73% (Branch) ✅
- governance_validation: passed ✅

### Riscos / observacoes (Iteracao 11)

- Mobile drawer fully functional for both visitor and authenticated states.
- Notification popover uses mock data as per FE-002 spec.
- Avatar click placeholder for FE-003 implemented.

## Iteracao 12 - Profile Sidebar (FE-003)

### Entregas concluidas (Iteracao 12)

- Profile Sidebar component with Drawer UI.
- Multi-role support via Chakra Tabs.
- Role-based navigation links.
- Navbar integration (Avatar click trigger).

### Onde foi entregue (Iteracao 12)

- `linkauto-frontend/src/components/ProfileSidebar.tsx`
- `linkauto-frontend/src/components/ProfileSidebar.test.tsx`
- `linkauto-frontend/src/components/Navbar.tsx`
- `linkauto-frontend/src/components/Navbar.test.tsx`

### Validacao executada (Iteracao 12)

- cycle_id: iteration-005
- red_command: `npm run test -- src/components/ProfileSidebar.test.tsx` ✅
- green_command: `npm run test -- src/components/ProfileSidebar.test.tsx` ✅
- coverage_pct: 100% (Line), 94% (Branch) ✅
- governance_validation: passed ✅

### Riscos / observacoes (Iteracao 12)

- Profile sidebar supports multi-role users with Chakra Tabs.
- Navbar integration tested and verified.
- Redirect after logout and multi-role logic fully covered by unit tests.

## Iteracao 13 - Home Sections (FE-005, FE-006)

### Entregas concluidas (Iteracao 13)

- Informative sections (Como Funciona, Para Alunos/Instrutores, Stats).
- Testimonials component with role-based tabs.
- Mock data for testimonials.
- Integration of all blocks into Home.tsx.

### Onde foi entregue (Iteracao 13)

- `linkauto-frontend/src/components/landing/InfoSections.tsx`
- `linkauto-frontend/src/components/landing/Testimonials.tsx`
- `linkauto-frontend/src/services/mockTestimonials.ts`
- `linkauto-frontend/src/pages/Home.tsx`

### Iteracao 13 - Home Sections (FE-005, FE-006)

- cycle_id: iteration-006
- red_command: `npm run test -- src/components/landing/InfoSections.test.tsx src/components/landing/Testimonials.test.tsx` ✅
- green_command: `npm run test -- src/components/landing/InfoSections.test.tsx src/components/landing/Testimonials.test.tsx` ✅
- coverage_pct: 100% (Line), 100% (Branch) ✅
- governance_validation: passed ✅

### Iteracao 14 - Mini FAQ (FE-005 extension)

- cycle_id: iteration-007
- red_command: `npm run test -- src/components/landing/FAQ.test.tsx` ✅
- green_command: `npm run test -- src/components/landing/FAQ.test.tsx` ✅
- coverage_pct: 100% (Line), 100% (Branch) ✅
- governance_validation: passed ✅

### Iteracao 15 - Bug Fixing (Known Issues #1-6)

- cycle_id: iteration-008
- task_id: ISSUE-FIX-ALL
- red_command: `npm run test` (Failing due to structural changes and missing affordance) ✅
- green_command: `npm run test` ✅
- coverage_pct: >= 80% ✅
- governance_validation: passed ✅

### Risks / observacoes (Iteracao 15)

- Resolved all 6 issues from `docs/known-issues.md`.
- Refactored `InfoSections.tsx`, `Testimonials.tsx`, `FAQ.tsx`, and `Login.tsx` for consistency and theme compatibility.
- Fixed `z-index` leaking issues for Leaflet maps and Navbar.
- Improved label association and accessibility in `Login.tsx`.
- Updated `Footer.test.tsx` to handle more specific queries.

### Risks / observacoes (Iteracao 14)

- Mini FAQ implemented with Accordion UI.
- All landing page sections from landpage_UX.md are now complete and integrated.

