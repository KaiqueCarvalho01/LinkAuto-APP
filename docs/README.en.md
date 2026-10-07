![LinkAuto Logo](images/LinkAuto-logo-square.webp)

# LinkAuto 🚗💨

A modern, mobile-first platform connecting student drivers with independent, certified driving instructors.

Languages:
- 🇧🇷 **PT-BR:** [README.md](../README.md)
- 🇺🇸 **US-EN:** [docs/README.en.md](README.en.md)

Quick Navigation:
- [Overview](#overview)
- [Visual Showcase](#visual-showcase)
- [Project Status](#project-status)
- [Operational Endpoints](#operational-api-endpoints)
- [Architecture & Stack](#architecture-and-stack)
- [How to Run](#how-to-run-locally)
- [Quality & Testing](#quality-and-testing)
- [Security & Hardening](SECURITY_TECHNIQUES.md)

![LinkAuto Banner](images/LinkAuto-banner.webp)

---

## Overview

**LinkAuto** organizes geolocation-based driving instructor discovery, regulatory verification, privacy-shielded public profiles, multi-slot scheduling with business rules, and mutual post-lesson reputation reviews.

### Consolidated Scope
- **Multi-Role User Domain:** Roles for `ALUNO` (Student), `INSTRUTOR` (Instructor), and `ADMIN`.
- **Hardened Authentication:** Short-lived JWT access tokens with silent cookie-based refresh tokens (`HttpOnly`, `Secure`).
- **Instructor Credential Validation (RN01):** Administrative verification workflow with Magic Bytes file inspection.
- **Anonymous Public Profiles (LGPD / RNF03):** Profile access via **human-friendly, entropy-salted slugs** (e.g. `/instructors/camila-rocha-mogi-mirim-8f2a`), shielding 100% of internal UUIDs and PII.
- **Scheduling Engine (RN02-RN04):** 1-hour slots, 2 consecutive hours minimum booking, state machine transitions, and automated 7-day penalty for cancellations under 24 hours.
- **Mutual Reviews & Async Messages:** Booking-specific conversation channel and 1-to-5 star rating system with atomic reputation recalculation.
- **Real-Time Dashboards:** Dedicated analytics and operational metrics for instructors and platform administrators.

### Canonical Documentation (Single Source of Truth)
- 📜 **Requirements & Business Rules:** [`docs/requirements.md`](requirements.md)
- 🎨 **Design System & UI Guidelines:** [`docs/DESIGN.md`](DESIGN.md)
- 🔌 **API Endpoint Specifications:** [`docs/BACKEND_ENDPOINT_REQUESTS.md`](BACKEND_ENDPOINT_REQUESTS.md)
- 🛡️ **Security Hardening Guides:** [`docs/SECURITY_TECHNIQUES.md`](SECURITY_TECHNIQUES.md) and [`docs/SECURITY_COMPARISON.md`](SECURITY_COMPARISON.md)
- 📖 **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs) (OpenAPI schema at `/openapi.json`)

---

## Visual Showcase

Key screens captured live during application runtime:

| Landing Page (Hero & Live Map Preview) | Geolocation Search with Leaflet |
| :---: | :---: |
| ![Home](images/showcase-home.png) | ![Search](images/showcase-search.png) |

| Public Instructor Profile (Slug & LGPD) | Management & Stats Dashboard |
| :---: | :---: |
| ![Instructor Profile](images/showcase-instructor-profile.png) | ![Dashboard](images/showcase-dashboard.png) |

---

## Project Status

### Progress by Phase

| Phase | State | Highlights & Coverage |
| :--- | :---: | :--- |
| **Phase 1 - Setup** | Completed | FastAPI routers, common envelopes, initial Docker Compose |
| **Phase 2 - Foundational** | Completed | JWT access/refresh, dev SQLite, booking state machine baseline |
| **Phase 3 - US1** | Completed | Registration, login, document uploads and Admin moderation |
| **Phase 4 - US2** | Completed | 1h slots, consecutive booking (min 2h), RN04 cancellation penalties |
| **Phase 5 - US3** | Completed | Async messages per booking, mutual reviews, 24h reminders, 8 SES emails |
| **Phase 6 - Polish & Hardening** | Completed | SlowAPI rate limits, security headers, magic bytes, correlation IDs |
| **Phase 7 - Frontend Integration** | Completed | 100% connected to live API, GPS/dropdown geolocation, 97 Vitest tests passing |
| **Phase 8 - Tooling & Stack Integration** | Completed | Migration to `uv`, `SQLModel 0.0.48`, `ty` typechecker, Alembic baseline, and VS Code workspace |

### Quality Gate Summary
- 🟢 **Backend:** **236 passed tests** in Pytest, 0 errors in `ty check`, 0 linter violations in `ruff check` (`ALL` rules).
- 🟢 **Frontend:** **102 passed tests** in Vitest, 0 TypeScript compiler errors (`npm run typecheck` in strict mode).

---

## Operational API Endpoints

All endpoints are implemented with strict Pydantic schemas and typed responses:

- **Foundation:**
  - `GET /health` — API health check
  - `GET /api/v1/foundation/ping` — Latency ping
- **Authentication:**
  - `POST /api/v1/auth/register` — Public registration (public ADMIN creation blocked)
  - `POST /api/v1/auth/login` — Login with rate-limiting and token issue
  - `POST /api/v1/auth/refresh` — Single-use refresh token rotation with reuse detection
  - `POST /api/v1/auth/logout` — Revokes the session's refresh token and clears the cookie
  - `POST /api/v1/auth/password-reset` — Password reset request
- **Users & Private Profiles:**
  - `GET /api/v1/users/me` — Current authenticated user profile
  - `PATCH /api/v1/users/me` — Profile update with Mass Assignment protection
- **Public Profiles (LGPD Shielding via Slugs):**
  - `GET /api/v1/instructors/{slug}/public` — Anonymous instructor profile with bio, rating, and DETRAN badge (404 if inactive)
  - `GET /api/v1/students/{slug}/public` — Anonymous student profile with completed lessons count and mutual ratings
- **Advanced Geolocation Search:**
  - `GET /api/v1/instructors/search` — Haversine search supporting specialty filters and multi-criteria sorting
- **Slots & Availability:**
  - `GET /api/v1/slots` — List available slots
  - `POST /api/v1/slots` — Create instructor 1-hour slots
  - `DELETE /api/v1/slots/{id}` — Delete unbooked slot
- **Bookings:**
  - `GET /api/v1/bookings` — User bookings (student or instructor)
  - `POST /api/v1/bookings` — Atomic booking request (requires >= 2 consecutive slots)
  - `PATCH /api/v1/bookings/{id}/cancel` — Cancellation with 24h rule and automated 7-day suspension
- **Messages & Reviews:**
  - `GET /api/v1/bookings/{id}/messages` — Booking conversation thread
  - `POST /api/v1/bookings/{id}/messages` — Send message with email notification
  - `POST /api/v1/bookings/{id}/reviews` — Mutual review allowed only for `REALIZADA` lessons
- **Administrative Governance & Stats:**
  - `GET /api/v1/admin/stats` — Global metrics (instructors, students, bookings)
  - `GET /api/v1/instructor/stats` — Individual instructor metrics (hours, lessons, unique students)
  - `GET /api/v1/admin/instructors/pending` — Pending verification queue
  - `POST /api/v1/admin/instructors/{id}/approve` — Approve instructor credentials
  - `POST /api/v1/admin/instructors/{id}/reject` — Reject with audit notes
- **Automation Jobs:**
  - `POST /api/v1/jobs/booking-reminder` — 24h pre-lesson reminder dispatch
  - `POST /api/v1/jobs/booking-timeout` — Auto-cancel PENDENTE bookings older than 24h
  - `POST /api/v1/jobs/booking-completion` — Auto-mark bookings REALIZADA 2h post-lesson

---

## Architecture and Stack

```text
.
├── LinkAuto-APP.code-workspace  # Multi-root VS Code workspace with dedicated per-app tooling
├── docs/                        # Canonical documentation (Requirements, Design, Endpoints, Security)
│   ├── archive/                 # Historical records and superseded drafting notes
│   └── images/                  # Brand identity and visual showcase screenshots
├── infra/                       # Multi-stage Dockerfiles and Docker Compose orchestrator
├── linkauto-backend/            # FastAPI service (SQLModel 0.0.48, uv, ty, Alembic, SQLite/PostgreSQL)
└── linkauto-frontend/           # React 19 SPA (Vite, Chakra UI v3, Tailwind CSS 4, Vitest)
```

- **Frontend:** React 19.2, Vite, Tailwind CSS 4, Chakra UI v3, React Router DOM 7, Leaflet, Vitest.
- **Backend:** Python 3.14 (managed by `uv`), FastAPI, SQLModel 0.0.48, Alembic, Pydantic v2, psycopg 3, Ruff, ty.
- **Databases:** SQLite with deterministic auto-seed for development; PostgreSQL + PostGIS in production.
- **Cloud Integrations:** AWS S3 (ephemeral credential storage) and AWS SES (transactional emails).

---

## How to Run Locally

### Option A: Docker Compose (Recommended) 🐳

Launch the full stack (Backend, Frontend, and Database) in the background with a single command:

```bash
docker compose -f infra/docker-compose.yml up -d
```

> [!TIP]
> For a complete guide on container commands, troubleshooting, and containerized test execution, see the **[Infrastructure & Docker Guide (infra/README.md)](../infra/README.md)**.

Available services:
- 🌐 **Frontend (Web App):** [http://localhost:5173](http://localhost:5173)
- 🔌 **Backend API (Swagger Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)
- 🩺 **API Healthcheck:** [http://localhost:8000/health](http://localhost:8000/health)

Pre-seeded development credentials:
- **Student:** `aluno@linkauto.com.br` / `password123` (Slug: `gabriel-silva-mogi-mirim-1a2b`)
- **Instructor:** `camila@linkauto.com.br` / `password123` (Slug: `camila-rocha-mogi-mirim-8f2a`)
- **Admin:** `admin@linkauto.com.br` / `password123`

---

### Option B: Native Environment

#### 1. Backend (`linkauto-backend`)
Requires [uv](https://docs.astral.sh/uv/):

```bash
cd linkauto-backend
uv sync                                            # Creates .venv and installs lockfile dependencies
uv run uvicorn app.main:app --reload --port 8000   # Starts development server with hot-reload
```

#### 2. Frontend (`linkauto-frontend`)
Requires Node.js 20+:

```bash
cd linkauto-frontend
npm install
npm run dev
```

#### 3. Development in VS Code
Open the [`LinkAuto-APP.code-workspace`](../LinkAuto-APP.code-workspace) file directly. VS Code will automatically use the `uv` virtual environment, Ruff linter, and `ty` language server for the backend, alongside ESLint and Node tooling for the frontend.

---

## Quality and Testing

### Backend (`linkauto-backend`)
```bash
cd linkauto-backend
uv run ty check              # Strict static type checking
uv run ruff check .          # Linting with ALL rules enabled
uv run ruff format --check . # Code formatting check
uv run pytest                # Runs all 236 unit, contract, and integration tests
```

### Frontend (`linkauto-frontend`)
```bash
cd linkauto-frontend
npm run typecheck            # Strict TypeScript compilation (exactOptionalPropertyTypes)
npm run lint                 # Static code analysis with ESLint
npm run test                 # Runs all 102 automated tests with Vitest
```

### E2E Testing and Visual Validation
End-to-End browser workflows and visual rendering checks are performed natively through the **Chrome DevTools MCP** (`@browser-testing-with-devtools`), enabling headless DOM inspection, viewport testing, and screenshot verification.
