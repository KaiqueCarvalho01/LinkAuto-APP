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

1. Start backend dependencies and API:
   - docker compose -f infra/docker-compose.yml up -d
2. Run database migrations:
   - cd linkauto-backend
   - alembic upgrade head
3. Seed demo data:
   - python scripts/seed_demo.py
4. Start frontend:
   - cd linkauto-frontend
   - npm install
   - npm run dev

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
