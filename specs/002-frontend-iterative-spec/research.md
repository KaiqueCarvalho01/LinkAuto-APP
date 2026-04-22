# Phase 0 Research - Frontend Iterative Delivery Guardrails

## Decision 1: Iteration sizing policy

- Decision: Use iteration slices limited to **max 4 tasks** or **1 user-story feature**.
- Rationale: Balances productivity and control in agent-assisted delivery; reduces oversized change sets while avoiding over-fragmentation.
- Alternatives considered:
  - Max 3 tasks: rejected due excessive fragmentation and handoff overhead.
  - No explicit cap: rejected due higher regression risk and weak predictability.

## Decision 2: XP/TDD quality gate as mandatory workflow

- Decision: Every implementation task must provide red-green evidence (failing test first, then passing test) and keep coverage >=80% on changed scope.
- Rationale: Brownfield frontend needs deterministic behavior protection and low technical debt growth.
- Alternatives considered:
  - Test-after implementation: rejected because it does not prove behavior-first validation.
  - Manual QA only: rejected due weak repeatability and regression detection.

## Decision 3: Mock-first integration boundary

- Decision: When endpoint is unavailable or not contracted, frontend must use explicit local fallback/mocks and document transition criteria.
- Rationale: Enables continuous frontend cadence while backend evolves in parallel.
- Alternatives considered:
  - Block frontend until backend readiness: rejected due throughput loss.
  - Create speculative endpoints immediately: rejected due contract drift risk.

## Decision 4: Endpoint-request governance in markdown

- Decision: Any new endpoint demand must be pre-registered in `endpoint-requests.md` with justification, impact, alternatives, and decision status.
- Rationale: Prevents premature API expansion and preserves contract clarity.
- Alternatives considered:
  - Ad-hoc chat decisions only: rejected due poor auditability.
  - Direct implementation without request artifact: rejected due governance gaps.

## Decision 5: Markdown-first operational memory

- Decision: Use `progressTracker-frontend.md` as mandatory per-iteration execution log and keep specs/checklists in markdown.
- Rationale: Improves memory reuse, lowers context overhead, and preserves verifiable execution history.
- Alternatives considered:
  - Tracking only in commit messages: rejected due low process visibility.
  - External tracker only: rejected due context fragmentation outside repository.

## Decision 6: Existing frontend toolchain baseline

- Decision: Keep current frontend stack/tooling unchanged for this feature: React + Chakra + Tailwind + Leaflet, Vitest + Playwright.
- Rationale: This feature is governance/process-oriented and should not introduce runtime stack changes.
- Alternatives considered:
  - Add new testing framework: rejected as unnecessary complexity.
  - Raise coverage globally in one step: rejected; current policy targets changed scope per iteration.

## Resolved Clarifications

- Iteration cap ambiguity resolved: **max 4 tasks OR 1 user-story feature per cycle**.
- Quality gate ambiguity resolved: **red-green evidence mandatory per task + >=80% changed-scope coverage**.
- Documentation boundary resolved: **markdown artifacts are mandatory; `progressTracker-frontend.md` is required per iteration update**.
- New endpoint ambiguity resolved: **request must be documented before implementation attempt**.
