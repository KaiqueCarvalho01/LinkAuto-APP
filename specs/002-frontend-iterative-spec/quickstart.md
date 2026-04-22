# Quickstart - Frontend Iterative Execution (XP + SDD)

## Goal

Execute one frontend iteration with:

- max 4 tasks OR 1 user-story feature,
- red-green evidence per task,
- >=80% coverage on changed scope,
- markdown traceability updates.

## Prerequisites

- Branch: `001-frontend-polishment`
- Active feature: `specs/002-frontend-iterative-spec`
- Node dependencies installed in `linkauto-frontend`

## Iteration Flow

### 1) Define slice boundary

- Choose either:
  - up to 4 tasks, or
  - 1 user-story feature slice.
- Confirm acceptance criteria before coding.

### 2) Confirm integration boundary

- For each API-dependent task:
  - If endpoint contracted and available: use contract.
  - If not contracted/available: use mock-first fallback.
- If new endpoint is required, create/update:
  - `specs/002-frontend-iterative-spec/endpoint-requests.md`

### 3) RED phase (mandatory)

Run failing test(s) first for the selected slice.

Example commands:

```bash
cd linkauto-frontend
npm run test -- src/path/to/test-file.test.tsx
```

Record red evidence (command + failure summary).

### 4) GREEN phase (mandatory)

Implement minimum code to pass the failing tests.

```bash
cd linkauto-frontend
npm run test -- src/path/to/test-file.test.tsx
```

Record green evidence (command + pass summary).

### 5) Validate quality gates

Run validation for the changed scope.

```bash
cd linkauto-frontend
npm run typecheck
npm run lint
npm run test
npm run test:coverage
npm run validate:governance
```

Accept iteration only when:

- tests for changed scope pass,
- coverage policy (>=80% changed scope) is satisfied,
- governance validation command passes,
- no unintended route/link regressions are introduced.

### 6) Update markdown traceability

Update:

- `progressTracker-frontend.md` (deliveries, commands, outcomes, risks)
- `specs/002-frontend-iterative-spec/endpoint-requests.md` (if applicable)

### 7) Close iteration

Checklist before closing:

- Slice respects max 4 tasks or 1 feature.
- Red-green evidence exists for each implemented task.
- Coverage gate satisfied.
- Markdown tracker updated.

## Suggested command bundle (per cycle)

```bash
cd linkauto-frontend && npm run typecheck && npm run lint && npm run test && npm run test:coverage && npm run validate:governance
```

## Notes

- Keep cycles intentionally small to reduce merge risk and technical debt.
- Prefer stable fallback behavior over speculative backend coupling.
