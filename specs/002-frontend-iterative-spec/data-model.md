# Data Model - Frontend Iterative Delivery Guardrails

## Entity: FrontendIterationSlice

- Purpose: Represents one implementation cycle in the frontend stream.
- Key fields:
  - id (string)
  - title (string)
  - scope_mode (enum: TASK_BATCH, USER_STORY_FEATURE)
  - max_items (integer; constrained by policy)
  - status (enum: PLANNED, IN_PROGRESS, VALIDATED, CLOSED)
  - started_at (datetime, optional)
  - closed_at (datetime, optional)
- Validation rules:
  - TASK_BATCH must contain 1..4 tasks.
  - USER_STORY_FEATURE must contain exactly 1 feature slice.

## Entity: TaskSlice

- Purpose: Minimal deliverable item within a FrontendIterationSlice.
- Key fields:
  - id (string)
  - iteration_id (FK -> FrontendIterationSlice.id)
  - description (string)
  - acceptance_criteria (list of strings)
  - status (enum: TODO, RED_DONE, GREEN_DONE, VERIFIED)
- Validation rules:
  - Must include objective acceptance criteria before implementation.
  - Must include linked test evidence to reach VERIFIED.

## Entity: RedGreenEvidence

- Purpose: Captures XP/TDD execution proof for one task.
- Key fields:
  - id (string)
  - task_id (FK -> TaskSlice.id)
  - red_test_command (string)
  - red_failure_summary (string)
  - green_test_command (string)
  - green_success_summary (string)
  - captured_at (datetime)
- Validation rules:
  - RED evidence required before GREEN evidence.
  - TaskSlice cannot be VERIFIED without both RED and GREEN evidence.

## Entity: CoverageGate

- Purpose: Captures coverage validation for changed scope in one iteration.
- Key fields:
  - id (string)
  - iteration_id (FK -> FrontendIterationSlice.id)
  - target_scope (string)
  - lines_pct (number)
  - branches_pct (number)
  - functions_pct (number)
  - statements_pct (number)
  - passed (boolean)
- Validation rules:
  - passed = true only when agreed threshold policy is satisfied for changed scope.

## Entity: IntegrationBoundary

- Purpose: Defines frontend/backend dependency behavior per capability.
- Key fields:
  - id (string)
  - capability (string)
  - contract_status (enum: CONTRACTED, NOT_CONTRACTED)
  - endpoint_reference (string, optional)
  - fallback_strategy (string)
  - transition_criteria (string)
- Validation rules:
  - NOT_CONTRACTED requires explicit fallback_strategy.
  - CONTRACTED requires endpoint_reference.

## Entity: EndpointRequestRecord

- Purpose: Registers a new endpoint demand before backend implementation.
- Key fields:
  - id (string; e.g., ER-001)
  - title (string)
  - date (date)
  - requester (string)
  - frontend_iteration (string)
  - related_user_story (string)
  - current_contract_gap (string)
  - proposal (object/text)
  - alternatives_evaluated (list of strings)
  - justification (string)
  - impact_summary (string)
  - status (enum: PROPOSED, IN_REVIEW, APPROVED, REJECTED, POSTPONED)
- Validation rules:
  - Must exist before endpoint implementation starts.
  - Must include alternatives and impact.

## Entity: FrontendExecutionLog

- Purpose: Stores per-iteration markdown execution trace in tracker.
- Key fields:
  - iteration_id (FK -> FrontendIterationSlice.id)
  - changed_files (list of strings)
  - validation_commands (list of strings)
  - validation_results (list of strings)
  - risks_notes (list of strings)
- Validation rules:
  - Must be published in markdown at iteration close.

## Relationships

- FrontendIterationSlice 1 -> N TaskSlice
- TaskSlice 1 -> N RedGreenEvidence
- FrontendIterationSlice 1 -> N CoverageGate
- FrontendIterationSlice 1 -> N IntegrationBoundary
- FrontendIterationSlice 1 -> N EndpointRequestRecord
- FrontendIterationSlice 1 -> 1 FrontendExecutionLog (logical per closed cycle)

## State Transitions

### FrontendIterationSlice

- PLANNED -> IN_PROGRESS: when implementation begins.
- IN_PROGRESS -> VALIDATED: when tests and coverage gates pass.
- VALIDATED -> CLOSED: when markdown tracker/log updates are complete.

### TaskSlice

- TODO -> RED_DONE: failing test evidence recorded.
- RED_DONE -> GREEN_DONE: minimal implementation passes tests.
- GREEN_DONE -> VERIFIED: acceptance criteria + coverage conditions satisfied.
