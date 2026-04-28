# Iteration Slice Template

Use this template at the start of each cycle.

## Iteration Metadata

- cycle_id:
- title:
- date_start:
- owner:
- scope_mode: TASK_BATCH | USER_STORY_FEATURE

## Scope Boundary

- selected_story: US1 | US2 | US3
- selected_items_count:
- policy_check:
  - [ ] TASK_BATCH uses 1 to 4 tasks
  - [ ] USER_STORY_FEATURE uses exactly 1 feature slice

## Selected Items

List each planned item with acceptance criteria.

1. item_id:
   - description:
   - acceptance_criteria:
2. item_id:
   - description:
   - acceptance_criteria:
3. item_id:
   - description:
   - acceptance_criteria:
4. item_id:
   - description:
   - acceptance_criteria:

## Route and Navigation Dependencies

- [ ] Route scaffold dependency checked before final UI tasks
- notes:

## Integration Boundary Snapshot

- requires_api_contract: yes | no
- fallback_required: yes | no
- contract_or_mock_reference:

## Ready-to-Start Gate

- [ ] Scope boundary complies with cycle policy
- [ ] Acceptance criteria are objective and testable
- [ ] Integration boundary is declared
- [ ] Red phase test targets are listed
