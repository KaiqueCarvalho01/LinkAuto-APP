# Tasks: Frontend Iterative Delivery Guardrails

**Input**: Design documents from /specs/002-frontend-iterative-spec/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included because the specification explicitly requires XP/TDD red-green evidence and coverage gates.

**Constitutional Compliance**: Compliance guardrails are tracked in dedicated checklist tasks to preserve V1 boundaries.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create reusable markdown artifacts and structure for iterative execution.

- [x] T001 Create iteration slice template in specs/002-frontend-iterative-spec/checklists/iteration-slice-template.md
- [x] T002 Create red-green evidence template in specs/002-frontend-iterative-spec/checklists/red-green-evidence-template.md
- [x] T003 [P] Create coverage gate template in specs/002-frontend-iterative-spec/checklists/coverage-gate-template.md
- [x] T004 [P] Create integration boundary template in specs/002-frontend-iterative-spec/checklists/integration-boundary-template.md
- [x] T005 Create iteration artifacts guide in specs/002-frontend-iterative-spec/iterations/README.md
- [x] T006 Create V1 scope guardrail checklist in specs/002-frontend-iterative-spec/checklists/v1-scope-guardrails.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared governance validation tooling required by all user stories.

**CRITICAL**: No user story work should begin before this phase is complete.

- [x] T007 Create governance module index in linkauto-frontend/src/features/iteration-governance/index.ts
- [x] T008 [P] Implement markdown log loader in linkauto-frontend/src/features/iteration-governance/logLoader.ts
- [x] T009 [P] Add markdown log loader tests in linkauto-frontend/src/features/iteration-governance/logLoader.test.ts
- [x] T010 Implement governance validation CLI in linkauto-frontend/scripts/validate-governance.mjs
- [x] T011 Wire governance validation script in linkauto-frontend/package.json
- [x] T012 Document governance CLI usage in specs/002-frontend-iterative-spec/quickstart.md

**Checkpoint**: Shared governance baseline is ready.

---

## Phase 3: User Story 1 - Planejar Incrementos Frontend Pequenos (Priority: P1) 🎯 MVP

**Goal**: Enforce small, well-scoped iteration slices and close each cycle with markdown traceability.

**Independent Test**: Validate one cycle that contains at most 4 tasks or one user-story feature, confirms route scaffold precedence, and records what/where/how in markdown.

### Tests for User Story 1

- [x] T013 [P] [US1] Add failing tests for slice-size policy in linkauto-frontend/src/features/iteration-governance/slicePolicy.test.ts
- [x] T014 [P] [US1] Add failing tests for route-scaffold planning rule in linkauto-frontend/src/features/iteration-governance/routePlanningRule.test.ts

### Implementation for User Story 1

- [x] T015 [US1] Implement slice-size validator in linkauto-frontend/src/features/iteration-governance/slicePolicy.ts
- [x] T016 [US1] Implement route-scaffold validator in linkauto-frontend/src/features/iteration-governance/routePlanningRule.ts
- [x] T017 [US1] Create first planned cycle record in specs/002-frontend-iterative-spec/iterations/iteration-001.md
- [x] T018 [US1] Update cycle closure traceability fields in progressTracker-frontend.md

**Checkpoint**: User Story 1 is independently plannable and auditable.

---

## Phase 4: User Story 2 - Garantir Qualidade com XP/TDD (Priority: P2)

**Goal**: Enforce red-green workflow and coverage thresholds for changed scope.

**Independent Test**: Validate that a task fails first, passes after implementation, and records changed-scope coverage >=80%.

### Tests for User Story 2

- [x] T019 [P] [US2] Add failing tests for red-before-green evidence in linkauto-frontend/src/features/iteration-governance/qualityGate.test.ts
- [x] T020 [P] [US2] Add failing tests for coverage threshold policy in linkauto-frontend/src/features/iteration-governance/coveragePolicy.test.ts

### Implementation for User Story 2

- [x] T021 [US2] Implement red-green evidence validator in linkauto-frontend/src/features/iteration-governance/qualityGate.ts
- [x] T022 [US2] Implement changed-scope coverage validator in linkauto-frontend/src/features/iteration-governance/coveragePolicy.ts
- [x] T023 [US2] Extend governance CLI to enforce quality gates in linkauto-frontend/scripts/validate-governance.mjs
- [x] T024 [US2] Record quality gate outputs for cycle 001 in specs/002-frontend-iterative-spec/iterations/iteration-001.md

**Checkpoint**: User Story 2 quality gates are independently enforceable.

---

## Phase 5: User Story 3 - Integrar Frontend com Backend sem Divergencia (Priority: P3)

**Goal**: Enforce mock-first fallback and endpoint-request governance before backend coupling.

**Independent Test**: Validate that API-dependent capabilities pick contract endpoints when available, fallback to mock otherwise, and require endpoint-request records before new backend demand.

### Tests for User Story 3

- [x] T025 [P] [US3] Add failing tests for mock-first decision logic in linkauto-frontend/src/features/iteration-governance/integrationBoundary.test.ts
- [x] T026 [P] [US3] Add failing tests for endpoint-request prerequisite rule in linkauto-frontend/src/features/iteration-governance/endpointRequestPolicy.test.ts

### Implementation for User Story 3

- [x] T027 [US3] Implement integration boundary resolver in linkauto-frontend/src/features/iteration-governance/integrationBoundary.ts
- [x] T028 [US3] Implement endpoint-request prerequisite validator in linkauto-frontend/src/features/iteration-governance/endpointRequestPolicy.ts
- [x] T029 [US3] Add capability endpoint-or-mock mapping section in specs/002-frontend-iterative-spec/contracts/frontend-iteration-governance.md
- [x] T030 [US3] Add endpoint request lifecycle example in specs/002-frontend-iterative-spec/endpoint-requests.md

**Checkpoint**: User Story 3 integration boundaries are independently enforceable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, documentation polish, and end-to-end validation across stories.

- [x] T031 [P] Consolidate governance command examples in specs/002-frontend-iterative-spec/quickstart.md
- [x] T032 [P] Cross-link governance workflow in docs/designs/landpage_UX.md
- [x] T033 Run full frontend validation bundle and log results in progressTracker-frontend.md
- [x] T034 Run e2e smoke and register evidence in progressTracker-frontend.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Setup and blocks all user stories.
- User Story phases (Phase 3 to Phase 5): depend on Foundational completion.
- Polish (Phase 6): depends on completion of the selected user stories.

### User Story Dependencies

- US1 (P1): starts immediately after Foundational and defines MVP workflow.
- US2 (P2): depends on Foundational and reuses US1 iteration artifacts for quality evidence.
- US3 (P3): depends on Foundational and can proceed after US1 templates are in use.

### Within Each User Story

- Tests must be written first and fail before implementation.
- Validation helpers before documentation integration.
- Story-specific docs updated before checkpoint close.

---

## Parallel Opportunities

- Setup: T003 and T004 can run in parallel.
- Foundational: T008 and T009 can run in parallel.
- US1: T013 and T014 can run in parallel.
- US2: T019 and T020 can run in parallel.
- US3: T025 and T026 can run in parallel.
- Polish: T031 and T032 can run in parallel.

---

## Parallel Example: User Story 1

- Run T013 and T014 together to define failing policy tests.
- After tests exist, run T015 and T016 in parallel if ownership is split.

## Parallel Example: User Story 2

- Run T019 and T020 together for red-phase quality tests.
- Implement T021 and T022 in parallel, then consolidate with T023.

## Parallel Example: User Story 3

- Run T025 and T026 together for fallback and endpoint-request rules.
- Implement T027 and T028 in parallel, then finalize docs via T029 and T030.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Deliver User Story 1 (Phase 3).
3. Validate independent test criteria for US1.
4. Stop for review/demo before moving to US2.

### Incremental Delivery

1. Foundation ready (Phase 1 plus Phase 2).
2. Deliver US1 and validate.
3. Deliver US2 and validate.
4. Deliver US3 and validate.
5. Execute Phase 6 for cross-cutting confidence.

### Parallel Team Strategy

1. Team A completes Setup and Foundational tasks.
2. Then parallelize by story: A on US1, B on US2, C on US3.
3. Merge at Phase 6 with shared validation evidence.

---

## Notes

- All tasks follow checklist format with Task ID, optional parallel marker, optional story label, and explicit file path.
- Keep iteration slices within max 4 tasks or 1 user-story feature at execution time.
- Use markdown artifacts as the source of truth for planning, execution evidence, and endpoint governance.

---

## Phase 7: Scaffold & Router (FE-008)

**Purpose**: Set up required placeholder pages and routing before navigation components.

- [ ] T035 [P] [FE-008] Add failing tests for scaffold pages rendering in linkauto-frontend/src/pages/ScaffoldPages.test.tsx
- [x] T036 [P] [FE-008] Create scaffold page components in linkauto-frontend/src/pages/ (Refactored to English)
- [x] T037 [FE-008] Register scaffold pages in linkauto-frontend/src/app/router.tsx (Refactored to English)
- [ ] T038 [FE-008] Record quality gate outputs for cycle 002 in specs/002-frontend-iterative-spec/iterations/iteration-002.md

## Phase 8: Visitor Navbar (FE-001)

**Purpose**: Implement the visitor navigation bar with responsive layout and dropdowns.

- [x] T039 [FE-001] Add failing tests for Navbar component (visitor state)
- [x] T040 [FE-001] Implement Navbar component and responsive Drawer for mobile
- [x] T041 [FE-001] Implement scroll-triggered shadow
- [ ] T042 [FE-001] Record quality gate outputs for cycle 003 in iteration-003.md

## Phase 9: Authenticated Navbar (FE-002)

**Purpose**: Implement the authenticated state for the Navbar with Notifications and User Avatar.

- [x] T043 [FE-002] Add failing tests for authenticated state in linkauto-frontend/src/components/Navbar.test.tsx
- [x] T044 [FE-002] Implement Notifications and Avatar component in linkauto-frontend/src/components/Navbar.tsx
- [x] T045 [FE-002] Implement missing mobile Drawer for visitor and authenticated modes
- [x] T046 [FE-002] Record quality gate outputs for cycle 004 in specs/002-frontend-iterative-spec/iterations/iteration-004.md

## Phase 10: Profile Sidebar (FE-003)

**Purpose**: Implement role-based Profile Sidebar Drawer.

- [x] T047 [FE-003] Add failing tests for ProfileSidebar component in linkauto-frontend/src/components/ProfileSidebar.test.tsx
- [x] T048 [FE-003] Implement ProfileSidebar component with role-based tabs and links in linkauto-frontend/src/components/ProfileSidebar.tsx
- [x] T049 [FE-003] Integrate ProfileSidebar with Navbar avatar click
- [x] T050 [FE-003] Record quality gate outputs for cycle 005 in specs/002-frontend-iterative-spec/iterations/iteration-005.md

## Phase 11: Informative Sections (FE-005)

**Purpose**: Implement landing page blocks for "Como Funciona", "Para Alunos/Instrutores" and "Stats".

- [x] T051 [FE-005] Add failing tests for InfoSections component in linkauto-frontend/src/components/landing/InfoSections.test.tsx
- [x] T052 [FE-005] Implement InfoSections component in linkauto-frontend/src/components/landing/InfoSections.tsx
- [x] T053 [FE-005] Integrate InfoSections into Home.tsx

## Phase 12: Testimonials (FE-006)

**Purpose**: Implement social proof section with role-based tabs.

- [x] T054 [FE-006] Add failing tests for Testimonials component in linkauto-frontend/src/components/landing/Testimonials.test.tsx
- [x] T055 [FE-006] Create mock data in linkauto-frontend/src/services/mockTestimonials.ts
- [x] T056 [FE-006] Implement Testimonials component in linkauto-frontend/src/components/landing/Testimonials.tsx
- [x] T057 [FE-006] Integrate Testimonials into Home.tsx
- [x] T058 [FE-005/FE-006] Record quality gate outputs for cycle 006 in specs/002-frontend-iterative-spec/iterations/iteration-006.md

## Phase 13: FAQ Section (FE-005 Extension)

**Purpose**: Implement Mini FAQ section at the bottom of the landing page.

- [ ] T059 [FE-005] Add failing tests for FAQ component in linkauto-frontend/src/components/landing/FAQ.test.tsx
- [ ] T060 [FE-005] Implement FAQ component in linkauto-frontend/src/components/landing/FAQ.tsx
- [ ] T061 [FE-005] Integrate FAQ into Home.tsx
- [ ] T062 [FE-005] Record quality gate outputs for cycle 007 in specs/002-frontend-iterative-spec/iterations/iteration-007.md
