# Tasks: LinkAuto User, Booking and Scheduling Domains

**Input**: Design documents from `/specs/001-user-booking-domains/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-v1-openapi.yaml

**Tests**: Test tasks are included because the specification defines mandatory testing scenarios and measurable success criteria.

**Constitutional Compliance**: This feature touches security, LGPD document lifecycle, scheduling rules, and V1 scope guardrails. Compliance tasks are mandatory.

**Stability Rule**: No phase starts before the previous phase is stable and validated.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3)
- Every task includes exact file path(s)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize monorepo runtime and project scaffolding for backend/frontend.

- [ ] T001 Create backend app skeleton modules in linkauto-backend/app/\_\_init\_\_.py, linkauto-backend/app/api/\_\_init\_\_.py, linkauto-backend/app/models/\_\_init\_\_.py, linkauto-backend/app/services/\_\_init\_\_.py, and linkauto-backend/app/schemas/\_\_init\_\_.py
- [ ] T002 Initialize backend project config and dependencies in linkauto-backend/pyproject.toml and linkauto-backend/app/core/config.py
- [ ] T003 [P] Create frontend API base client and env binding in linkauto-frontend/src/services/httpClient.js and linkauto-frontend/src/services/config.js
- [ ] T004 [P] Create environment and local runtime bootstrap in infra/docker-compose.yml, linkauto-backend/.env.example, and linkauto-frontend/.env.example
- [ ] T005 Create migration bootstrap and base metadata wiring in linkauto-backend/alembic/env.py and linkauto-backend/alembic/versions/0001_foundation.py
- [ ] T006 Create implementation compliance evidence file in specs/001-user-booking-domains/compliance.md

**Checkpoint**: Setup stable, local stack starts, and foundational coding can begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core platform capabilities required before any user story.

**CRITICAL**: No user story work can begin until this phase is complete and stable.

- [ ] T007 Create shared ORM base with uuidv7 and audit timestamps in linkauto-backend/app/models/base.py
- [ ] T008 [P] Implement standard API envelope, pagination, and error schema in linkauto-backend/app/schemas/common.py
- [ ] T009 [P] Implement bcrypt password hashing and JWT access/refresh primitives in linkauto-backend/app/core/security.py
- [ ] T010 [P] Implement authentication and RBAC dependencies in linkauto-backend/app/api/deps/authn.py and linkauto-backend/app/api/deps/authz.py
- [ ] T011 Implement notification abstraction (SES adapter plus event dispatcher) in linkauto-backend/app/services/notification_service.py
- [ ] T012 Implement Booking domain core state machine and transition guards in linkauto-backend/app/domain/booking.py
- [ ] T013 Implement atomic slot reservation and first-write-wins locking service in linkauto-backend/app/services/booking_lock_service.py
- [ ] T014 Implement booking automation scheduler shell for 24h timeout and +2h completion in linkauto-backend/app/services/booking_scheduler.py
- [ ] T015 Implement foundational API router registration and versioned base path in linkauto-backend/app/api/v1/\_\_init\_\_.py and linkauto-backend/app/main.py
- [ ] T016 Add foundational contract validation for envelope/auth/conflict semantics in linkauto-backend/tests/contract/test_foundation_contract.py
- [ ] T017 Add foundational integration validation for Booking state transitions in linkauto-backend/tests/integration/test_booking_state_machine.py

**Checkpoint**: Foundation stable; Booking core invariants are enforced before story work.

---

## Phase 3: User Story 1 - Manage Multi-Role Accounts and Profiles (Priority: P1) 🎯 MVP Part A

**Goal**: Users can authenticate and manage role-based profiles; instructor visibility is gated by admin validation.

**Independent Test**: Create users with Student/Instructor/multi-role profiles, validate profile persistence, and verify non-approved instructors are hidden from search.

### Tests for User Story 1

- [ ] T018 [P] [US1] Add contract tests for /auth/* (including refresh token cookie contract) and /users/me in linkauto-backend/tests/contract/test_us1_auth_profile_contract.py
- [ ] T019 [P] [US1] Add integration tests for multi-role profile behavior and hidden instructors in linkauto-backend/tests/integration/test_us1_profiles_visibility.py
- [ ] T056 [P] [US1] Add integration tests for credential upload size and MIME whitelist validations in linkauto-backend/tests/integration/test_us1_document_upload_validation.py

### Implementation for User Story 1

- [ ] T020 [P] [US1] Create User, StudentProfile, and InstructorProfile models in linkauto-backend/app/models/user.py
- [ ] T021 [P] [US1] Create InstructorDocument model and repository helpers in linkauto-backend/app/models/instructor_document.py
- [ ] T022 [US1] Implement auth service (register/login/refresh/password reset trigger) with refresh token cookie `HttpOnly`/`Secure`/`SameSite` in linkauto-backend/app/services/auth_service.py
- [ ] T023 [US1] Implement role-aware profile service for /users/me in linkauto-backend/app/services/profile_service.py
- [ ] T024 [US1] Implement auth and users API endpoints in linkauto-backend/app/api/v1/auth.py and linkauto-backend/app/api/v1/users.py
- [ ] T025 [US1] Implement admin instructor validation workflow (approve/reject plus SES) in linkauto-backend/app/services/admin_validation_service.py
- [ ] T026 [US1] Implement S3 credential document purge after validation in linkauto-backend/app/services/document_cleanup_service.py
- [ ] T057 [US1] Implement backend validation for credential upload limit (10MB/file) and MIME whitelist in linkauto-backend/app/services/instructor_document_service.py
- [ ] T027 [US1] Implement admin instructor endpoints in linkauto-backend/app/api/v1/admin_instructors.py
- [ ] T028 [US1] Implement frontend login/profile/admin dashboard wiring in linkauto-frontend/src/pages/Login.jsx, linkauto-frontend/src/pages/Profile.jsx, and linkauto-frontend/src/pages/InstructorDashboard.jsx
- [ ] T029 [US1] Implement frontend session and route guards by role in linkauto-frontend/src/state/sessionStore.js and linkauto-frontend/src/app/router.jsx

**Checkpoint**: US1 stable and independently testable.

---

## Phase 4: User Story 2 - Create and Govern Bookings with Scheduling Rules (Priority: P1) 🎯 MVP Part B (Core)

**Goal**: Students create bookings only with valid consecutive slots; booking lifecycle and penalties follow domain rules.

**Independent Test**: Validate booking creation, conflict handling, timeouts, confirmation/cancellation policies, and automatic penalties.

### Tests for User Story 2

- [ ] T030 [P] [US2] Add contract tests for /instructors/*/slots, /bookings, /bookings/{id}/confirm, /bookings/{id}/cancel, and /admin/bookings/{id}/override-status in linkauto-backend/tests/contract/test_us2_booking_contract.py
- [ ] T031 [P] [US2] Add integration tests for RN02, RN03, RN04, penalty window, first-write-wins, and `IntegrityError` to 409 mapping in linkauto-backend/tests/integration/test_us2_booking_rules.py

### Implementation for User Story 2

- [ ] T032 [P] [US2] Create Slot and booking_slots persistence models in linkauto-backend/app/models/slot.py and linkauto-backend/app/models/booking_slot.py
- [ ] T033 [P] [US2] Create Booking and StudentPenalty models in linkauto-backend/app/models/booking.py
- [ ] T058 [US2] Add database constraints for RN03 slot uniqueness and booking slot consistency in linkauto-backend/alembic/versions/0002_booking_constraints.py
- [ ] T034 [US2] Implement slot service with 1h invariant and non-overlap checks in linkauto-backend/app/services/slot_service.py
- [ ] T035 [US2] Implement booking service (create/list/detail/confirm/cancel) with atomic reservation in linkauto-backend/app/services/booking_service.py
- [ ] T059 [US2] Implement `IntegrityError` handling mapped to standardized 409 conflict envelope in linkauto-backend/app/api/v1/slots.py and linkauto-backend/app/api/v1/bookings.py
- [ ] T036 [US2] Implement booking timeout and +2h completion jobs with admin override hooks in linkauto-backend/app/jobs/booking_jobs.py
- [ ] T037 [US2] Implement slots and bookings API endpoints in linkauto-backend/app/api/v1/slots.py and linkauto-backend/app/api/v1/bookings.py
- [ ] T060 [US2] Implement admin booking override endpoint and service in linkauto-backend/app/api/v1/admin_bookings.py and linkauto-backend/app/services/admin_booking_service.py
- [ ] T038 [US2] Implement approved-only geosearch service with SQLite fallback and PostGIS-ready strategy in linkauto-backend/app/services/instructor_search_service.py
- [ ] T039 [US2] Implement instructor search endpoint in linkauto-backend/app/api/v1/instructor_search.py
- [ ] T040 [US2] Implement frontend search and booking flows in linkauto-frontend/src/pages/SearchPage.jsx, linkauto-frontend/src/pages/LessonDetails.jsx, and linkauto-frontend/src/pages/MyLessons.jsx
- [ ] T041 [US2] Add booking cascade regression suite to protect downstream stories from Booking core changes in linkauto-backend/tests/integration/test_booking_cascade_regression.py

**Checkpoint**: US2 stable and independently testable; Booking core considered stable baseline for dependent flows.

---

## Phase 5: User Story 3 - Exchange Messages, Reviews, and Email Notifications (Priority: P2)

**Goal**: Instructor/student communication, review lifecycle gating, and notification events are complete.

**Independent Test**: Post booking messages, confirm notifications, reject reviews before REALIZADA, and accept mutual reviews after REALIZADA.

### Tests for User Story 3

- [ ] T042 [P] [US3] Add contract tests for /bookings/{id}/messages, /bookings/{id}/reviews, and /instructors/{id}/reviews in linkauto-backend/tests/contract/test_us3_message_review_contract.py
- [ ] T043 [P] [US3] Add integration tests for message timeline, SES triggers, and review gating in linkauto-backend/tests/integration/test_us3_message_review_flow.py

### Implementation for User Story 3

- [ ] T044 [P] [US3] Create BookingMessage and Review models in linkauto-backend/app/models/booking_message.py and linkauto-backend/app/models/review.py
- [ ] T045 [US3] Implement booking message thread service and pagination in linkauto-backend/app/services/booking_message_service.py
- [ ] T046 [US3] Implement message thread API endpoints in linkauto-backend/app/api/v1/booking_messages.py
- [ ] T047 [US3] Implement review service with REALIZADA gate and uniqueness checks in linkauto-backend/app/services/review_service.py
- [ ] T048 [US3] Implement review create/list endpoints for booking and instructor profile in linkauto-backend/app/api/v1/reviews.py
- [ ] T049 [US3] Implement event-driven SES handlers for booking/message/review notifications in linkauto-backend/app/services/notification_handlers.py
- [ ] T050 [US3] Implement frontend booking thread and post-lesson rating UX in linkauto-frontend/src/components/RatingModal.jsx, linkauto-frontend/src/components/ConfirmationModal.jsx, and linkauto-frontend/src/pages/LessonDetails.jsx

**Checkpoint**: US3 stable and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, observability, compliance evidence, and demo readiness.

- [ ] T051 [P] Update demo and operational docs for phase stability gates in specs/001-user-booking-domains/quickstart.md and README.md
- [ ] T052 [P] Add end-to-end happy-path smoke test for instructor-admin-student flow in linkauto-backend/tests/integration/test_e2e_happy_path.py
- [ ] T053 Harden structured logging and trace IDs for booking-critical flows in linkauto-backend/app/core/logging.py
- [ ] T054 Validate constitutional guardrails and record evidence in specs/001-user-booking-domains/compliance.md
- [ ] T055 Run full backend and frontend verification suites via linkauto-backend/tests and linkauto-frontend/tests and document result in specs/001-user-booking-domains/quickstart.md
- [ ] T061 [P] Add contract tests for ISO 8601 UTC serialization in booking/slot/message envelopes in linkauto-backend/tests/contract/test_datetime_utc_contract.py
- [ ] T062 [P] Implement shared UTC datetime serialization helpers and schema adapters in linkauto-backend/app/schemas/datetime.py and linkauto-backend/app/schemas/common.py

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1.
- Phase 3 (US1): depends on stable completion of Phase 2.
- Phase 4 (US2): depends on stable completion of Phase 3.
- Phase 5 (US3): depends on stable completion of Phase 4.
- Phase 6 (Polish): depends on stable completion of Phases 3, 4, and 5.

### User Story Dependencies

- US1: starts after Foundational phase is stable.
- US2: starts after US1 is stable, because booking operations require authenticated roles and validated instructor visibility.
- US3: starts after US2 is stable, because messaging and review gating depend on Booking lifecycle correctness.
- Domain dependency chain for implementation and validation: User -> Profile -> Slot -> Booking -> BookingMessage -> Review.

### Booking Core Dependency Rule

- Booking is the system core aggregate. Any change in linkauto-backend/app/domain/booking.py, linkauto-backend/app/services/booking_service.py, or linkauto-backend/app/jobs/booking_jobs.py requires re-running T041, T052, and T061 before advancing phase.

---

## Parallel Execution Examples

### US1 Parallel Example

```bash
Task T018 and Task T019 can run together.
Task T020 and Task T021 can run together.
```

### US2 Parallel Example

```bash
Task T030 and Task T031 can run together.
Task T032 and Task T033 can run together.
```

### US3 Parallel Example

```bash
Task T042 and Task T043 can run together.
Task T044 can run in parallel with frontend prep in Task T050 after API contracts are stable.
```

---

## Implementation Strategy

### MVP First (Stable Core Path)

1. Complete Phase 1 and Phase 2.
2. Complete US1 and validate independently.
3. Complete US2 (Booking core) and validate independently.
4. Stop and run regression checks before starting US3.

### Incremental Delivery

1. Deliver increment A: US1 (identity and profile correctness).
2. Deliver increment B: US2 (core booking and scheduling rules).
3. Deliver increment C: US3 (messaging, reviews, notifications).
4. Finish with Phase 6 hardening and demo readiness.

### Quality Gates

- No phase starts before previous phase stability criteria are met.
- Booking-core changes always trigger cascade regression validation before progression.
- No promotion to US3 without contract-complete review APIs (create and list) and admin override booking endpoint.
- No phase completion without UTC datetime contract checks and upload validation checks passing.
