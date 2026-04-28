# Iteration 004 - Authenticated Navbar (FE-002)

## Iteration Metadata

- cycle_id: iteration-004
- title: FE-002 Authenticated Navbar
- date_start: 2026-04-25
- date_end: 2026-04-25
- owner: copilot
- scope_mode: USER_STORY_FEATURE

## Scope Boundary

- selected_story: FE-002
- selected_items_count: 1
- policy_check:
  - [x] USER_STORY_FEATURE uses exactly 1 feature slice

## Selected Items

1. item_id: FE-002
   - description: Navbar (Estado Autenticado)
   - acceptance_criteria:
     - Substituir CTAs de visitante por Notificações e Avatar.
     - Notificações com badge e Popover (mock local).
     - Avatar exibe primeiro nome (oculto em mobile).
     - Mobile Drawer funcional para visitante e autenticado.

## Route and Navigation Dependencies

- [x] Route scaffold dependency checked before final UI tasks
- notes: All routes scaffolded in FE-008.

## Integration Boundary Snapshot

- requires_api_contract: no
- fallback_required: yes
- contract_or_mock_reference: Local mock for notifications list.

## Ready-to-Start Gate

- [x] Scope boundary complies with cycle policy
- [x] Acceptance criteria are objective and testable
- [x] Integration boundary is declared
- [x] Red phase test targets are listed

## RED-GREEN Evidence

### Navbar Authenticated

- red_command: npm run test -- src/components/Navbar.test.tsx
- red_failure_summary: Authenticated tests failed because sessionStore was not imported and notifications/avatar elements were missing.
- green_command: npm run test -- src/components/Navbar.test.tsx
- green_success_summary: All 6 tests passed, covering visitor dropdowns, authenticated state, notifications popover, and mobile drawer.

## Coverage Gate

- target_scope: src/components/Navbar.tsx
- command: npm run test:coverage -- src/components/Navbar.test.tsx
- required_threshold_pct: 70
- lines_pct: 100
- branches_pct: 73.33
- functions_pct: 100
- statements_pct: 100
- passed: true
- policy_note: 100% line coverage achieved. Branch coverage at 73% is acceptable due to Chakra v3 responsive object props being difficult to isolate as branches in JSDOM.

## Delivery Summary

### What was delivered (Iteracao 004)

- Authenticated Navbar with Notifications Popover and User Avatar.
- Functional Mobile Drawer for both visitor and authenticated states.
- Mock notification list for FE-002.

### Where it was delivered (Iteracao 004)

- src/components/Navbar.tsx
- src/components/Navbar.test.tsx

### How it was validated (Iteracao 004)

- npm run test -- src/components/Navbar.test.tsx
- npm run test:coverage -- src/components/Navbar.test.tsx

## Risks and Notes

- Mobile drawer implementation is required to fulfill the "responsive" acceptance criteria.
