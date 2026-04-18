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
| Phase 4 - US2 | Pending |
| Phase 5 - US3 | Pending |
| Phase 6 - Polish | Pending |

### What is already implemented

Backend:

- FastAPI with versioned router under /api/v1 and healthcheck at /health
- Standard success/error envelopes and validation error handling
- JWT access/refresh, RBAC, and HttpOnly/Secure/SameSite refresh cookie
- Full US1 flow: register, login, profile, approved public instructor listing
- Admin instructor approval/rejection endpoints
- Credential upload with 10MB limit and MIME whitelist (PDF/JPEG/PNG)
- Notification v1 event catalog (in-memory gateway in current runtime)

Frontend:

- React 19 + Vite with session and role-based protected routes
- Connected login, profile, and admin instructor validation views
- HTTP client with credentials, bearer token support, and normalized error handling

> [!NOTE]
> Current US1 runtime uses an in-memory store (IdentityStore), suitable for contract and integration flow validation.
> US2/US3 phases complete persistent Booking-centric behavior end-to-end.

## Contract vs runtime

The OpenAPI contract already defines slots, booking, messaging, and review endpoints.
The currently operational runtime endpoints are:

- /health
- /api/v1/foundation/*
- /api/v1/auth/*
- /api/v1/users/me
- /api/v1/users/public-instructors
- /api/v1/admin/instructors*
- /api/v1/instructors/{id}/documents

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

Current notable coverage includes:

- Foundation envelope/auth/conflict contracts
- Auth + users/me contract and flow
- Booking domain state machine
- Upload validation (MIME/10MB)
- Approved instructor visibility behavior

## Immediate roadmap

Next phases:

- US2: slots, booking lifecycle, penalties, conflict behavior, admin booking override
- US3: booking-thread messages, review creation after REALIZADA, full notification events
- Polish: hardening, Booking core cascade regression, final validation

Dependency chain enforced by implementation flow:

User -> Profile -> Slot -> Booking -> BookingMessage -> Review
