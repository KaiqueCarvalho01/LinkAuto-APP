# V1 Scope Guardrails Checklist

Use this checklist before closing each cycle.

## Out-of-Scope Blocking Rules

- [ ] No payment intermediation or transaction value display added
- [ ] No real-time chat or WebSocket dependency introduced
- [ ] No push/SMS/WhatsApp channel introduced
- [ ] No PDF/CSV export feature introduced
- [ ] No automated moderation capability added

## Security and Domain Invariants

- [ ] Instructor visibility remains blocked until admin validation
- [ ] Existing auth/session policy remains unchanged unless formally approved
- [ ] No backend contract changes outside approved domain artifacts

## Delivery Governance

- [ ] Cycle respects max 4 tasks or 1 user-story feature
- [ ] Red-green evidence exists for each implemented task
- [ ] Coverage policy for changed scope is met
- [ ] Markdown traceability updated in progressTracker-frontend.md
- [ ] New endpoint demand has prior request record in endpoint-requests.md
