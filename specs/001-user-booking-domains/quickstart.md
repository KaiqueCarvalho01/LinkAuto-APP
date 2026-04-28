# Quickstart: LinkAuto MVP Demo

## Objective

1. Instructor registers and uploads documents.
2. Admin validates instructor.
3. Instructor publishes slots.
4. Student searches, books, and confirms reservation flow.
5. Student and instructor exchange booking-thread messages.

## Prerequisites

- Docker and Docker Compose
- Node.js 20+
- Python 3.11+
- AWS credentials for SES and S3 test environment

## Environment

Create environment files before running services.

### Backend .env

- APP_ENV=development
- DATABASE_URL=sqlite:///./app.db
- RESET_SQLITE_ON_STARTUP=true
- `CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`
- JWT_SECRET=change-me
- JWT_ACCESS_MINUTES=15
- JWT_REFRESH_DAYS=7
- AWS_REGION=...
- AWS_ACCESS_KEY_ID=...
- AWS_SECRET_ACCESS_KEY=...
- S3_BUCKET=...
- SES_FROM_EMAIL=...

### Frontend .env

- VITE_API_BASE_URL=<http://localhost:8000/api/v1>

## Run Local Stack

1. Start backend and frontend:
   - docker compose -f infra/docker-compose.yml up -d
2. Backend startup in development will recreate SQLite (`app.db`) automatically when `RESET_SQLITE_ON_STARTUP=true`.
3. Install frontend dependencies:
   - cd linkauto-frontend
   - npm install

## E2E Smoke (automated)

1. Install Playwright browsers (once):
   - cd linkauto-frontend
   - npm run e2e:install
2. Install system libs on Linux hosts (when required):
   - cd linkauto-frontend
   - sudo npx playwright install-deps
   - Arch/WSL2 (AUR):
     - sudo pacman -Syy
     - yay -S --needed atk at-spi2-core libxcomposite libxdamage libxfixes libxrandr mesa libxkbcommon alsa-lib
3. Run smoke e2e:
   - npm run e2e

Default targets:

- Frontend: `http://127.0.0.1:5173`
- API: `http://127.0.0.1:8000/api/v1`

Optional overrides:

- `E2E_BASE_URL`
- `E2E_API_BASE_URL`

Smoke coverage:

- Register student account through API.
- Login through UI.
- Navigate search -> lesson details -> booking request.
- Validate redirect to `/agendamentos`.

## Demo Script

### Step A: Instructor onboarding

1. Open registration page and create instructor account.
2. Upload DETRAN and criminal record documents.
3. Verify pending status message and notification email.

### Step B: Admin validation

1. Login as admin.
2. Open pending instructor list.
3. Review uploaded documents.
4. Approve instructor and verify approval email.

### Step C: Instructor agenda

1. Login as approved instructor.
2. Create one-hour slots for same day in consecutive sequence.
3. Confirm slots are visible as available.

### Step D: Student booking flow

1. Register/login as student.
2. Search instructor by map/list.
3. Open profile and create booking with >=2 consecutive slots.
4. Instructor confirms booking.
5. Verify student confirmation email.

### Step E: Booking chat and review visibility

1. Open booking thread and post asynchronous messages.
2. Verify message notification emails.
3. Move booking to REALIZADA (scheduler or admin override).
4. Verify review submission is blocked before REALIZADA and allowed after.

## Validation Checklist

- Health check returns success.
- Instructor remains hidden before admin approval.
- Booking fails for non-consecutive or <2 slots.
- Concurrent booking on same slots returns one success and one conflict.
- Late cancellation (<=24h) applies 7-day student booking block.
- Documents are deleted from S3 after validation flow completes.

## Known Dev/Prod Differences

- Dev geosearch uses SQLite-compatible distance filtering.
- Prod geosearch uses PostgreSQL + PostGIS indexes.
- Email delivery in dev can be sandboxed depending on SES account limits.
