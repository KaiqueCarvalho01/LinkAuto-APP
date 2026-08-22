---
name: linkauto-core
description: >-
  Skill Router and Capability Map for LinkAuto. Directly references and orchestrates all installed specialist skills mapped to LinkAuto's stack (React 19, TypeScript strict, Chakra UI v3, FastAPI, SQLAlchemy 2.0, TDD, Playwright).
---

# 🚗 LinkAuto — Specialist Skills Router & Execution Matrix

This file is the **central skill index and orchestrator** for the **LinkAuto** project. It maps the project's technology stack and agile lifecycle directly to the specialized skills installed in the environment.

Before executing tasks, AI agents should consult this index and inspect the corresponding skill file via `view_file` to apply specialized knowledge without requiring manual user re-prompting.

---

## 🧭 1. Technology & Domain Mapping

### 🟢 1.1 Frontend & UI Engineering
**Stack**: React 19.2, TypeScript 5.9 (strict), Chakra UI v3 (`@chakra-ui/react@3.x`), Tailwind CSS 4, Leaflet.

| Specialist Skill | When to Read / Trigger | Absolute Path |
| :--- | :--- | :--- |
| **`@frontend-ui-engineering`** | Creating or refactoring UI components, pages, responsive layouts, forms and states. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/frontend-ui-engineering/SKILL.md` |
| **`@frontend-design`** | Visual hierarchy, distinctive styling, modern palettes, hero sections and landing aesthetics. | `/home/gabrieldnsilva/.agents/skills/frontend-design/SKILL.md` |
| **`@react-composition-patterns`** | Chakra UI v3 Composition API (`*.Root`, `*.Trigger`, `*.Content`), compound components and slot patterns. | `/home/gabrieldnsilva/.agents/skills/react-composition-patterns/SKILL.md` |
| **`@react-best-practices`** | React 19 hook lifecycles, state isolation, `useEffect` cleanup guards (`isMounted`) and memoization. | `/home/gabrieldnsilva/.agents/skills/react-best-practices/SKILL.md` |
| **`@web-design-guidelines`** | UI/UX audits, typography, micro-interactions, responsive touch targets and design consistency. | `/home/gabrieldnsilva/.agents/skills/web-design-guidelines/SKILL.md` |
| **`@accessibility`** | WCAG 2.1 compliance, keyboard navigation, `aria-label`, contrast and screen-reader accessibility. | `/home/gabrieldnsilva/.agents/skills/accessibility/SKILL.md` |

---

### 🔵 1.2 Backend, Database & API Contracts
**Stack**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, SQLite (dev) / PostgreSQL + PostGIS (prod).

| Specialist Skill | When to Read / Trigger | Absolute Path |
| :--- | :--- | :--- |
| **`@api-and-interface-design`** | Designing REST endpoints, Pydantic schemas, HTTP status codes, pagination and error envelopes. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/api-and-interface-design/SKILL.md` |
| **`@security-and-hardening`** | Defense-in-Depth validation, rate-limiting (SlowAPI), token security (JWT), SQL injection protection and CORS. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/security-and-hardening/SKILL.md` |
| **`@security-best-practices`** | Secrets handling, safe middleware configurations, OWASP Top 10 mitigation and audit logging. | `/home/gabrieldnsilva/.agents/skills/security-best-practices/SKILL.md` |

---

### 🧪 1.3 Testing, Quality Assurance & Debugging
**Stack**: Vitest, React Testing Library, Pytest, Starlette TestClient, Playwright, Chrome DevTools.

| Specialist Skill | When to Read / Trigger | Absolute Path |
| :--- | :--- | :--- |
| **`@test-driven-development`** | Every feature, bugfix, or contract change. Drives RED -> GREEN -> REFACTOR cycles. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/test-driven-development/SKILL.md` |
| **`@debugging-and-error-recovery`** | Investigating failing tests, runtime exceptions, 500 errors, or async lifecycle issues. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/debugging-and-error-recovery/SKILL.md` |
| **`@code-review-and-quality`** | Multi-axis evaluation of changes (correctness, architecture, security, performance) before delivery. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/code-review-and-quality/SKILL.md` |
| **`@playwright-skill`** | Writing or maintaining End-to-End browser smoke tests (`linkauto-frontend/tests/e2e/`). | `/home/gabrieldnsilva/.agents/skills/playwright-skill/SKILL.md` |
| **`@browser-testing-with-devtools`** | Inspecting DOM, network requests, console errors, or performance profiles in a real browser. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/browser-testing-with-devtools/SKILL.md` |
| **`@performance-optimization`** | Query optimization (N+1 reduction), bundle size tuning, memoization and load performance. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/performance-optimization/SKILL.md` |

---

### 📋 1.4 Agile Workflow, Planning & Governance
**Approach**: XP / Lean TDD (no SDD overhead), Markdown Trackers.

| Specialist Skill | When to Read / Trigger | Absolute Path |
| :--- | :--- | :--- |
| **`@planning-and-task-breakdown`** | Breaking complex user stories into small, ordered, testable steps. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/planning-and-task-breakdown/SKILL.md` |
| **`@incremental-implementation`** | Delivering multi-file features safely in verifiable vertical slices. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/incremental-implementation/SKILL.md` |
| **`@code-simplification`** | Refactoring working code for clarity, modularity, and removing unnecessary cognitive load. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/code-simplification/SKILL.md` |
| **`@documentation-and-adrs`** | Recording major architectural decisions, trade-offs, or public API modifications in `docs/`. | `/home/gabrieldnsilva/.gemini/config/plugins/agent-skills/skills/documentation-and-adrs/SKILL.md` |

---

## 🔄 2. Execution Protocol by Lifecycle Phase

```
┌───────────────────────────────┐
│ 1. TASK SYNC & BREAKDOWN      │ ──> @planning-and-task-breakdown, @incremental-implementation
│    (Read Tracker & Docs)      │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 2. RED (Write Failing Test)   │ ──> @test-driven-development, @api-and-interface-design
│    (Pytest / Vitest)          │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 3. GREEN (Implement Feature)  │ ──> @frontend-ui-engineering, @react-composition-patterns,
│    (Minimal Working Code)     │     @security-and-hardening
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 4. REFACTOR & QUALITY GATE    │ ──> @code-simplification, @code-review-and-quality,
│    (100% Tests Pass)          │     @performance-optimization
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 5. TRACKER UPDATE & LOGGING   │ ──> Update progressTracker.md / progressTracker-frontend.md
└───────────────────────────────┘
```

---

## ⚡ 3. Quick Command Reference

- **Frontend Validation**: `cd linkauto-frontend && npm run typecheck && npm run test`
- **Backend Validation**: `cd linkauto-backend && .venv/bin/python -m pytest`
- **Frontend E2E**: `cd linkauto-frontend && npm run e2e`
