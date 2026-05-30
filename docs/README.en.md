# LinkAuto (US-EN)

![LinkAuto Logo](images/LinkAuto-logo-square.webp)

Mobile-first platform that connects students and autonomous driving instructors.

Language:

- PT-BR: [../README.md](../README.md)
- US-EN: [README.en.md](README.en.md)

Quick navigation:

- [Overview](#overview)
- [Current status](#current-status)
- [Run locally](#run-locally)
- [Quality and tests](#quality-and-tests)

![LinkAuto Banner](images/LinkAuto-banner.webp)

> [!IMPORTANT]
> This document reflects the current runtime state of the repository.
> The functional and contractual source-of-truth for V1 is under ../specs/001-user-booking-domains.

## Overview

LinkAuto organizes instructor discovery, authentication, admin validation, and (next phase) full booking flow with business rules centered on Booking.

Consolidated V1 functional scope:

- Multi-role user model (ALUNO, INSTRUTOR, ADMIN)
- Authentication with access token + cookie-based refresh token
- Instructor admin validation workflow
- Credential document upload with security validation
- OpenAPI contract for slots, bookings, messages, and reviews

Primary references:

- [../specs/001-user-booking-domains/spec.md](../specs/001-user-booking-domains/spec.md)
- [../specs/001-user-booking-domains/plan.md](../specs/001-user-booking-domains/plan.md)
- [../specs/001-user-booking-domains/tasks.md](../specs/001-user-booking-domains/tasks.md)
- [../specs/001-user-booking-domains/contracts/api-v1-openapi.yaml](../specs/001-user-booking-domains/contracts/api-v1-openapi.yaml)

## Current status

### Phase progress

| Phase | Status |
| --- | --- |
| Phase 1 - Setup | Completed |
| Phase 2 - Foundational | Completed |
| Phase 3 - US1 | Completed |
| Phase 4 - US2 | Completed |
| Phase 5 - US3 | Completed |
| Phase 6 - Polish | Completed |

### What is already implemented

Backend:

- **Foundational Infrastructure (Phase 1-2):** Versioned routing under `/api/v1`, standard envelopes, SQLite support, robust JWT access/refresh, and high-security RBAC.
- **US1 (Register, Login & Admin):** Complete signup/login workflow, credential upload with security validations, and admin approval/rejection dashboard.
- **US2 (Booking & Slots):** Slot management (1h slots), request consecutive slots (minimum 2), state machine for booking transitions, and automatic 7-day penalty for cancellation under 24h of the lesson start time.
- **US3 (Chat, Reviews & Notifications):** Cronologically ordered booking messages, mutual reviews for realized lessons with atomic instructor rating recaps (`rating_avg`/`rating_count`), UTC ISO 8601 serializations ("Z"), automated 24h lesson reminder cron, and a catalog of 8 e-mail event notifications.
- **Phase 6 (Polish & Hardening):** SlowAPI rate-limiting on authentication endpoints (login, register, reset, refresh), HTTP security headers middleware, magic bytes binary signature validations, production fail-fast configuration, isolated and resilient gateway exception handling, and structured security auditing logs with Trace/Correlation IDs.

Frontend:

- React 19 + Vite with session and role-protected routing.
- Integrated flows for Login, map-based (Leaflet) search and list of approved instructors, booking slot picker with consecutive slot guards, lesson dashboard with status timelines, and admin validation boards.
- HTTP client with credentials support, bearer tokens, and standardized error handling.

## Runtime Endpoints

All endpoints described in the OpenAPI contract are 100% operational in the LinkAuto runtime:

- **Foundation:** `/health`, `/api/v1/foundation/ping`
- **Auth:** `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/password-reset`
- **Users & Profiles:** `/api/v1/users/me`, `/api/v1/users/public-instructors`
- **Slots:** `/api/v1/slots`, `/api/v1/slots/instructor/{id}`
- **Bookings:** `/api/v1/bookings`, `/api/v1/bookings/{id}/cancel`
- **Messages & Reviews:** `/api/v1/bookings/{id}/messages`, `/api/v1/bookings/{id}/reviews`
- **Admin Validation:** `/api/v1/admin/instructors/pending`, `/api/v1/admin/instructors/{id}/approve`, `/api/v1/admin/instructors/{id}/reject`
- **Jobs Cron:** `/api/v1/jobs/booking-reminder`, `/api/v1/jobs/booking-timeout`, `/api/v1/jobs/booking-completion`

## Architecture and stack

- Frontend: React 19, Vite, Tailwind CSS 4, React Router
- Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: SQLite (dev) and PostgreSQL + PostGIS (production target)
- Integrations: AWS S3 (documents) and AWS SES (notifications)

Available diagrams:

- [diagrams/architecture-overview.svg](diagrams/architecture-overview.svg)
- [diagrams/use-cases-v1.svg](diagrams/use-cases-v1.svg)
- [diagrams/uml-class-diagram-v1.svg](diagrams/uml-class-diagram-v1.svg)
- [diagrams/booking-sequence.svg](diagrams/booking-sequence.svg)

## Repository structure

```text
.
├── docs/
├── infra/
├── linkauto-backend/
├── linkauto-frontend/
├── specs/
│   └── 001-user-booking-domains/
└── README.md
```

## Run locally

### Option A (recommended): Docker Compose

```bash
docker compose -f infra/docker-compose.yml up -d
```

In development mode, backend startup now rebuilds the local SQLite database on each boot (`RESET_SQLITE_ON_STARTUP=true`), recreating `app.db` and base schema automatically.

Services:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### Option B: Separate backend and frontend

Backend:

```bash
cd ../linkauto-backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd ../linkauto-frontend
npm install
npm run dev
```

> [!TIP]
> For auth flow validation with refresh cookie, keep both frontend and backend running with credentials enabled (already set in the HTTP client).

## E2E testing (manual + automated)

Initial setup (one time):

```bash
cd ../linkauto-frontend
npm install
npm run e2e:install
```

System dependencies (Linux, when required):

```bash
cd ../linkauto-frontend
sudo npx playwright install-deps
```

For Arch Linux (including custom WSL2 setups), prefer installing via `yay`/AUR:

```bash
sudo pacman -Syy
yay -S --needed atk at-spi2-core libxcomposite libxdamage libxfixes libxrandr mesa libxkbcommon alsa-lib
```

Run automated smoke flow (login + search + booking request):

```bash
cd ../linkauto-frontend
npm run e2e
```

Suggested manual flow (with backend and frontend running):

1. Open `/login`.
2. Register an `ALUNO` account through `/api/v1/auth/register` (or use an existing account).
3. Authenticate and confirm redirect to `/buscar`.
4. Open an instructor from `Agendar`, select 2 consecutive slots, and confirm redirect to `/agendamentos`.

Optional e2e environment variables:

- `E2E_BASE_URL` (default: `http://127.0.0.1:5173`)
- `E2E_API_BASE_URL` (default: `http://127.0.0.1:8000/api/v1`)

## Quality and tests

Backend (contract + integration):

```bash
cd ../linkauto-backend
. .venv/bin/activate
ruff check .
pytest
```

Frontend (baseline quality checks):

```bash
cd ../linkauto-frontend
npm run lint
npm run build
```

Frontend (e2e smoke):

```bash
cd ../linkauto-frontend
npm run e2e
```

Current notable coverage includes:

- Foundation envelope/auth/conflict contracts
- Auth + users/me contract and flow
- Booking domain state machine
- Upload validation (MIME/10MB)
- Approved instructor visibility behavior
