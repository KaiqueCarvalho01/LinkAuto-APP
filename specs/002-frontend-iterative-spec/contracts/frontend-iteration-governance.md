# Contract - Frontend Iteration Governance Interface

## Purpose

Define the minimum interface between planning and implementation cycles for frontend delivery in this feature.

## Contract Scope

This contract governs each frontend cycle executed under:

- `specs/002-frontend-iterative-spec/spec.md`
- `progressTracker-frontend.md`
- `specs/002-frontend-iterative-spec/endpoint-requests.md`

## Input Contract (cycle start)

Each cycle must declare:

- cycle_id
- scope_mode: TASK_BATCH or USER_STORY_FEATURE
- scope_items: max 4 tasks, or exactly 1 user-story feature
- acceptance_criteria per scope item
- integration boundary per API-dependent scope item

## Execution Contract (during cycle)

Each implemented scope item must produce:

- Red evidence (failing automated test)
- Green evidence (passing automated test)
- Validation command history for changed scope

## Quality Gate Contract (cycle validation)

Cycle can only move to closed state when:

- all selected scope items are validated
- changed-scope automated coverage meets agreed threshold policy
- no known broken route/navigation introduced by cycle changes

## Documentation Contract (mandatory markdown output)

At cycle close, updates are required in markdown:

- `progressTracker-frontend.md`:
  - what was delivered
  - where it was delivered (files/paths)
  - how it was validated (commands + outcomes)
  - risks/notes

If new endpoint demand appears:

- register request before implementation in:
  - `specs/002-frontend-iterative-spec/endpoint-requests.md`

## Out-of-contract actions

The following actions violate this contract:

- cycle execution above scope limit
- implementation without red-green evidence
- backend endpoint implementation without prior endpoint request record
- closing cycle without markdown traceability update

## Capability Mapping (Mock vs Contract)

This section actively logs current capabilities and their status per this feature iteration.

- **Instructor Search**: `CONTRACTED` (Ref: `GET /api/v1/instructors`)
- **Booking Creation**: `NOT_CONTRACTED` (Fallback: `USE_MOCK` locally until slot creation endpoint is contracted)
- **Profile Fetch**: `NOT_CONTRACTED` (Fallback: `USE_MOCK` until session integration finalized)

## Change Control

Any modification to this contract must be reflected in:

- `specs/002-frontend-iterative-spec/spec.md`
- `specs/002-frontend-iterative-spec/plan.md`
- `specs/002-frontend-iterative-spec/checklists/requirements.md`
