# Data Model: LinkAuto User, Booking and Scheduling Domains

## Entity: User

- Primary key: id (uuidv7)
- Fields: email (unique), password_hash, roles[], is_active, created_at, updated_at
- Rules:
  - email unique across all users.
  - password_hash required and never plain text.
  - roles[] contains one or more of ALUNO, INSTRUTOR, ADMIN.

## Entity: StudentProfile

- Primary key: user_id (FK -> User.id, 1:1)
- Fields: full_name, phone, city, state, license_type, avatar_url
- Rules:
  - Required when roles[] includes ALUNO.
  - license_type enum: NENHUMA, A, B, AB, C, D, E, EM_PROCESSO.

## Entity: InstructorProfile

- Primary key: user_id (FK -> User.id, 1:1)
- Fields: full_name, phone, city, state, bio, specialties[], price_per_hour, avatar_url, detran_status, action_radius_km, latitude, longitude, rating_avg, rating_count
- Rules:
  - Required when roles[] includes INSTRUTOR.
  - detran_status enum: PENDENTE, APROVADO, REJEITADO.
  - Public search visibility only when detran_status = APROVADO.
  - action_radius_km default 10.

## Entity: InstructorDocument

- Primary key: id (uuidv7)
- Foreign keys: instructor_id (FK -> InstructorProfile.user_id), reviewed_by (FK -> User.id, nullable)
- Fields: detran_credential_url, criminal_record_url, uploaded_at, reviewed_at
- Rules:
  - URLs point to S3 objects.
  - Document files must be deleted from S3 after validation completes.

## Entity: Slot

- Primary key: id (uuidv7)
- Foreign key: instructor_id (FK -> InstructorProfile.user_id)
- Fields: starts_at, ends_at, status
- Rules:
  - status enum: DISPONIVEL, RESERVADO, BLOQUEADO.
  - Duration invariant: ends_at - starts_at = 1h.
  - No overlapping slots for same instructor.

## Entity: Booking

- Primary key: id (uuidv7)
- Foreign keys: student_id (FK -> StudentProfile.user_id), instructor_id (FK -> InstructorProfile.user_id)
- Fields: status, location_description, latitude, longitude, created_at, confirmed_at, cancelled_at, cancelled_by, cancellation_reason
- Relation: M:N with Slot through booking_slots table (booking_id, slot_id).
- Rules:
  - Minimum 2 consecutive slots, same instructor, same day (RN02).
  - Atomic reservation for slot_ids with first-write-wins conflict behavior.
  - cancelled_by enum: ALUNO, INSTRUTOR, SISTEMA.
  - Late student cancellation (<=24h) applies 7-day booking block.

## Entity: BookingMessage

- Primary key: id (uuidv7)
- Foreign keys: booking_id (FK -> Booking.id), sender_id (FK -> User.id)
- Fields: content, created_at
- Rules:
  - One linear thread per booking.
  - Messages are asynchronous (no realtime transport requirement).

## Entity: Review

- Primary key: id (uuidv7)
- Foreign keys: booking_id (FK -> Booking.id), reviewer_id (FK -> User.id), reviewed_id (FK -> User.id)
- Fields: rating, comment, created_at
- Rules:
  - rating range 1..5.
  - Unique constraint on (booking_id, reviewer_id, reviewed_id).
  - Allowed only if booking status is REALIZADA.

## Supporting Policy Entity: StudentPenalty (derived or persisted)

- Key: student_id (FK -> StudentProfile.user_id)
- Fields: blocked_until, reason, created_at
- Rule:
  - New bookings blocked while now < blocked_until.

## Booking State Machine

- PENDENTE -> CONFIRMADA: instructor approves within 24h.
- PENDENTE -> CANCELADA: instructor rejects or timeout job after 24h.
- CONFIRMADA -> REALIZADA: scheduler job after lesson end + 2h buffer.
- CONFIRMADA -> CANCELADA: student or instructor cancellation, with RN04 penalty logic.
- Admin override: allowed for correcting terminal state after exceptional cases.

## Notification Event Catalog (SES)

- Instructor registered, waiting validation.
- Instructor approved/rejected by admin.
- New pending booking for instructor.
- Lesson reminder 24h before.
- Booking confirmed for student.
- Booking canceled for student/instructor.
- New booking message.
- New review received.
