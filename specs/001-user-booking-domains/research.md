# Research: LinkAuto User, Booking and Scheduling Domains

## Decision 1: Keep monorepo split as linkauto-backend plus linkauto-frontend

- Decision: Use existing repository structure with backend and frontend isolated by responsibility.
- Rationale: Minimizes migration work and aligns with requested MVP phases.
- Alternatives considered: Single app repo; rejected because backend and frontend concerns are already separated.

## Decision 2: Local dev runtime with Docker Compose (API plus SQLite plus Adminer)

- Decision: Provide Compose for reproducible local startup and quick demo setup.
- Rationale: Supports classroom demo consistency and quick reset.
- Alternatives considered: Manual local startup only; rejected due to higher setup variance.

## Decision 3: SQLite in dev, Postgres/PostGIS in prod with geospatial fallback

- Decision: In dev, compute distance with application-level geo filtering over instructor coordinates.
- Rationale: Constitution requires SQLite in dev without PostGIS while preserving search behavior.
- Alternatives considered: Enabling PostGIS in dev; rejected by constitutional stack constraint.

## Decision 4: UUIDv7 default for all new domain IDs

- Decision: All new domain entities use UUIDv7 as the default identifier format.
- Rationale: Provides sortable IDs and consistent traceability across services.
- Alternatives considered: Mixed UUIDv4/int strategy; rejected due to cross-domain inconsistency.

## Decision 5: Booking concurrency with atomic first-write-wins

- Decision: Use atomic slot reservation transaction; first committed booking wins, loser gets conflict.
- Rationale: Prevents overbooking and yields deterministic behavior.
- Alternatives considered: Queue retry model; rejected for added complexity in MVP.

## Decision 6: Booking completion automation with +2h buffer and admin override

- Decision: Scheduled job transitions CONFIRMADA to REALIZADA at least 2h after final slot end.
- Rationale: Matches clarified behavior and keeps operational recovery path via admin override.
- Alternatives considered: Manual-only completion; rejected due to operational overhead.

## Decision 7: Late cancellation penalty is fixed and automatic

- Decision: Student cancellation at <=24h triggers 7-day booking block.
- Rationale: Converts RN04 into enforceable and testable domain behavior.
- Alternatives considered: Configurable policy; rejected for MVP simplicity.

## Decision 8: Messaging model remains asynchronous per booking thread

- Decision: One message thread per booking, no realtime transport.
- Rationale: Meets constitutional constraints and keeps architecture simple.
- Alternatives considered: WebSocket chat; rejected as out-of-scope for V1.

## Decision 9: SES notifications via domain events

- Decision: Emit explicit notification events from auth/admin/booking/message/review flows.
- Rationale: Keeps API responses predictable while ensuring notification coverage.
- Alternatives considered: Inline email calls in controllers; rejected to reduce coupling.

## Decision 10: Demo-first phased implementation

- Decision: Preserve phased rollout from foundation to polish, prioritizing happy path.
- Rationale: Supports visible progress and de-risks classroom demo execution.
- Alternatives considered: Big-bang implementation; rejected due to higher integration risk.
