# Feature Specification: LinkAuto User, Booking and Scheduling Domains

**Feature Branch**: `001-run-feature-hook`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "LinkAuto — Specification (Dominios de Usuarios, Agenda, Agendamento, Mensagens, Avaliacoes e Notificacoes)"

## Clarifications

### Session 2026-04-16

- Q: Quando um agendamento `CONFIRMADA` for cancelado com 24h ou menos de antecedencia, qual deve ser o comportamento oficial da V1? → A: Permitir cancelamento e aplicar penalidade automatica ao aluno.
- Q: Para a transicao `CONFIRMADA -> REALIZADA`, qual politica oficial da V1 devemos fixar? → A: Automatica por job apos `ends_at` da ultima slot com buffer de 2h, com possibilidade de override pelo Admin.
- Q: Qual penalidade automatica deve ser aplicada ao aluno quando ele cancela uma booking `CONFIRMADA` com `<=24h` de antecedencia? → A: Bloqueio de novas reservas por 7 dias corridos.
- Q: Quando duas solicitacoes concorrentes tentam reservar os mesmos slots `DISPONIVEL`, qual politica oficial da V1? → A: First-write-wins com validacao atomica de slots no backend; a outra requisicao falha com erro de conflito.
- Q: Para IDs dos dominios desta feature, qual regra oficial da V1? → A: Todos os IDs de entidades de dominio novas devem ser uuidv7 por padrao.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Manage Multi-Role Accounts and Profiles (Priority: P1)

As a platform user, I can maintain one account with one or more roles (Student, Instructor, Admin), with the correct profile data for each role, so I can participate in the platform safely and according to my role.

**Why this priority**: No booking, visibility, or moderation flow works without consistent identity and role/profile boundaries.

**Independent Test**: Can be fully tested by creating and updating accounts with role combinations and validating profile requirements and visibility rules.

**Acceptance Scenarios**:

1. **Given** a user account with role Student, **When** the user completes mandatory student profile fields, **Then** the profile is saved and available for booking actions.
2. **Given** a user account with role Instructor and pending credential review, **When** the account is queried in public search, **Then** the instructor is not visible.
3. **Given** a user account with both Student and Instructor roles, **When** the user updates one profile, **Then** the other role profile remains intact and valid.

---

### User Story 2 - Create and Govern Bookings with Scheduling Rules (Priority: P1)

As a student, I can create bookings only when at least two consecutive one-hour slots are available for the same instructor on the same day, and both parties can progress the booking through valid lifecycle states.

**Why this priority**: Booking and schedule integrity is the core business capability and must enforce RN02, RN04, and transition safety.

**Independent Test**: Can be fully tested by creating valid and invalid slot selections, approving/rejecting bookings, and verifying the booking state machine and cancellation rules.

**Acceptance Scenarios**:

1. **Given** two consecutive available one-hour slots for an instructor, **When** a student requests a booking, **Then** the booking is created as pending with both slots reserved.
2. **Given** non-consecutive or insufficient slots, **When** a student attempts to book, **Then** booking creation is blocked with a clear validation error.
3. **Given** a pending booking older than 24 hours without instructor decision, **When** timeout processing runs, **Then** the booking transitions to canceled by system and both parties are notified.
4. **Given** a confirmed booking, **When** cancellation occurs with more than 24 hours before start time, **Then** cancellation is allowed without penalty status.
5. **Given** a confirmed booking, **When** a student cancels with 24 hours or less before start time, **Then** cancellation is allowed and an automatic student penalty is applied.
6. **Given** a confirmed booking whose last slot has ended, **When** 2 hours have elapsed and completion job runs, **Then** booking transitions automatically to `REALIZADA` unless admin override sets a different terminal state.
7. **Given** a student account penalized by late cancellation, **When** the student attempts a new booking during penalty window, **Then** booking creation is blocked until 7 full days have elapsed.
8. **Given** two concurrent booking requests for the same available slots, **When** both are submitted nearly simultaneously, **Then** only the first committed request succeeds and the second fails with conflict.

---

### User Story 3 - Exchange Messages, Reviews, and Email Notifications (Priority: P2)

As a student or instructor, I can exchange asynchronous messages per booking, receive event-driven email updates, and submit mutual reviews only after booking status `REALIZADA`.

**Why this priority**: Communication, trust, and reputation complete the service loop after booking.

**Independent Test**: Can be fully tested by posting booking-thread messages, triggering each listed email event, and attempting review submission before and after status `REALIZADA`.

**Acceptance Scenarios**:

1. **Given** an active booking thread, **When** either party posts a message, **Then** the message is appended chronologically to that booking thread and notification is sent.
2. **Given** a booking not in status `REALIZADA`, **When** a review is submitted, **Then** the review is rejected.
3. **Given** a booking in status `REALIZADA`, **When** each side submits one review for the other, **Then** each review is accepted once and duplicate reviewer-reviewed submissions are blocked.

---

### Edge Cases

- User has multiple roles but only one profile payload is provided during update.
- Instructor coordinates or action radius are missing while instructor profile is set to active.
- Two selected slots cross midnight; they are consecutive by time but not on the same day.
- Booking cancellation happens exactly at the 24-hour boundary (must be treated as penalty case).
- Instructor confirms after timeout cancellation has already occurred.
- Completion job runs late or retries after transient failure.
- Penalty window expiry occurs mid-day and booking attempts happen exactly at expiry timestamp.
- Two booking transactions race for the same slots and one must fail deterministically.
- Duplicate slot IDs are included in a booking request.
- A second review attempt is made for the same reviewer-reviewed pair in one booking.
- Instructor documents are approved or rejected after files were already removed from storage.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST maintain a base user entity with unique email, account status, timestamps, and one-or-more roles.
- **FR-002**: System MUST store credentials only as secure password hashes and never as plain text.
- **FR-003**: System MUST allow a single user to hold multiple roles simultaneously.
- **FR-004**: System MUST require and persist student profile fields when role includes Student.
- **FR-005**: System MUST require and persist instructor profile fields when role includes Instructor.
- **FR-006**: System MUST keep instructors hidden from public search while credential status is pending or rejected.
- **FR-007**: System MUST support credential document records for instructors with upload and review audit fields.
- **FR-008**: System MUST remove credential documents from storage after validation workflow completion.
- **FR-009**: System MUST maintain one-hour slot records with explicit available/reserved/blocked status.
- **FR-010**: System MUST enforce slot duration of exactly one hour.
- **FR-011**: System MUST allow booking creation only with at least two consecutive slots for the same instructor on the same day.
- **FR-012**: System MUST validate booking minimum-slot rules in both client and server flows.
- **FR-013**: System MUST maintain booking lifecycle states: `PENDENTE`, `CONFIRMADA`, `REALIZADA`, `CANCELADA`.
- **FR-014**: System MUST enforce booking transitions only through approved state-machine paths.
- **FR-015**: System MUST auto-cancel pending bookings not decided within 24 hours and mark cancellation source as system.
- **FR-016**: System MUST record cancellation metadata, including actor and optional reason.
- **FR-017**: System MUST allow student cancellation with 24 hours or less before start time and MUST apply automatic penalty status to the student account.
- **FR-018**: System MUST maintain one asynchronous message thread per booking with chronological entries.
- **FR-019**: System MUST allow review creation only when booking status is `REALIZADA`.
- **FR-020**: System MUST enforce one review per reviewer-reviewed pair per booking.
- **FR-021**: System MUST trigger email notifications for all defined events in registration, validation, booking, messaging, and review flows.
- **FR-022**: System MUST expose API endpoints under a versioned base path and require bearer authentication for protected operations.
- **FR-023**: System MUST return standardized success and error envelopes and support page/page_size pagination defaults.
- **FR-024**: System MUST represent dates and times in ISO 8601 UTC format across API responses.
- **FR-025**: System MUST use uuidv7 as default ID format for all new domain entities in this feature.
- **FR-026**: System MUST transition confirmed bookings to `REALIZADA` automatically using a scheduled job at least 2 hours after the end time of the last booked slot, and MUST allow admin override for correction.
- **FR-027**: System MUST enforce a fixed 7-day booking block for students who cancel confirmed bookings with 24 hours or less before start time.
- **FR-028**: System MUST enforce atomic slot reservation with first-write-wins behavior for concurrent booking attempts and MUST return a conflict error for losing requests.

_Note_: Penalty-free cancellation remains valid only when cancellation occurs with more than 24 hours before start time.

### Constitutional Constraints _(mandatory)_

- **CC-001**: Feature MUST NOT introduce payment intermediation, payment processing, transaction value display, or instructor financial history.
- **CC-002**: Feature MUST keep messaging asynchronous for V1 and MUST NOT require real-time chat or WebSockets.
- **CC-003**: Feature MUST preserve instructor invisibility in search until Admin validation.
- **CC-004**: Feature MUST preserve security invariants where applicable: bcrypt password storage, no plain text passwords, JWT access token + refresh token model.
- **CC-005**: Feature MUST preserve scheduling/business invariants where applicable: 1h slots, minimum 2h booking, penalty-free cancellation only with >24h notice, and mutual rating only after `REALIZADA`.
- **CC-006**: Feature MUST remain within approved V1 stack unless a constitution amendment is approved.

### Out of Scope _(mandatory)_

- Payment processing, intermediation, or financial ledger features.
- Real-time chat (WebSockets) in V1.
- Push, SMS, or WhatsApp notifications in V1.
- PDF/CSV export for lesson history in V1.
- Automated moderation of ratings in V1.

If any out-of-scope item becomes required, the spec MUST request a constitution amendment before implementation planning.

### Key Entities _(include if feature involves data)_

- **User**: Base identity record with unique login, role set, lifecycle timestamps, and account activation status.
- **Student Profile**: Student-specific contact, location, license stage/type, and optional avatar.
- **Instructor Profile**: Instructor-specific identity, coverage area, specialties, DETRAN status, profile media, and reputation aggregates.
- **Instructor Document**: Validation artifact metadata for instructor credential and criminal record submissions.
- **Slot**: Atomic one-hour instructor availability unit with reservable status.
- **Booking**: Reservation aggregate connecting student, instructor, slots, location, lifecycle timestamps, and cancellation metadata.
- **Booking Message**: Single-thread asynchronous communication record scoped to one booking.
- **Review**: Post-completion rating/comment record constrained by reviewer-reviewed uniqueness within a booking.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of booking creation attempts with fewer than two consecutive slots are rejected with explicit validation feedback.
- **SC-002**: 100% of instructors not approved by admin remain excluded from public search results.
- **SC-003**: 99% of booking state transition attempts follow allowed lifecycle paths, with invalid transitions blocked.
- **SC-004**: 100% of review submissions when booking status is not `REALIZADA` are rejected.
- **SC-005**: At least 95% of valid booking flows (search-to-pending) are completed by users in under 3 minutes.
- **SC-006**: 100% of configured notification event types are emitted to intended recipients.
- **SC-007**: 100% of concurrent reservation tests for identical slots result in exactly one successful booking and one conflict response.

## Assumptions

- Admin moderation is available daily to process instructor validation decisions.
- Existing platform authentication and authorization services are available for role-based access checks.
- Geolocation can be provided by user device or manually when needed.
- Payments continue to occur outside the platform in V1.
- Booking transition to `REALIZADA` uses scheduled automation after lesson end plus 2-hour buffer, with admin override when needed.
