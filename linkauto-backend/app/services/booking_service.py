from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking, BookingSlot, CancelledBy
from app.models.slot import Slot, SlotStatus
from app.models.user import User
from app.services.penalty_service import PenaltyService
from app.services.notification_service import NotificationService, NotificationPayload, NotificationEvent

CANCELLATION_NOTICE_HOURS = 24


class SlotValidationError(ValueError):
    pass


class PenalizedStudentError(ValueError):
    pass


class BookingService:
    def __init__(
        self,
        db: Session,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._db = db
        self._penalty = PenaltyService(db)
        self._notification_service = notification_service

    def create_booking(
        self,
        student_id: str,
        instructor_id: str,
        slot_ids: list[str],
        location_description: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Booking:
        # RN04: penalized student cannot book
        if self._penalty.is_penalized(student_id):
            raise PenalizedStudentError("Student is currently penalized and cannot create bookings")

        # RN02: minimum 2 slots
        if len(slot_ids) < 2:
            raise SlotValidationError("Booking requires minimum 2 consecutive slots (RN02)")

        # Fetch and validate slots
        slots = (
            self._db.query(Slot)
            .filter(Slot.id.in_(slot_ids))
            .order_by(Slot.starts_at)
            .all()
        )

        if len(slots) != len(slot_ids):
            raise SlotValidationError("One or more slot IDs not found")

        # All slots must belong to same instructor
        if not all(s.instructor_id == instructor_id for s in slots):
            raise SlotValidationError("All slots must belong to the specified instructor")

        # All slots must be available
        unavailable = [s for s in slots if s.status != SlotStatus.DISPONIVEL.value]
        if unavailable:
            raise SlotValidationError(f"Slots not available: {[s.id for s in unavailable]}")

        # RN02: slots must be consecutive (each starts when previous ends)
        for i in range(1, len(slots)):
            if slots[i].starts_at != slots[i - 1].ends_at:
                raise SlotValidationError(
                    "Slots must be consecutive — each slot must start when the previous ends"
                )

        # Reserve slots atomically (first-write-wins)
        for slot in slots:
            slot.status = SlotStatus.RESERVADO.value
        self._db.flush()

        # Create booking
        booking = Booking(
            student_id=student_id,
            instructor_id=instructor_id,
            status=BookingStatus.PENDENTE.value,
            location_description=location_description,
            latitude=latitude,
            longitude=longitude,
        )
        self._db.add(booking)
        self._db.flush()

        # Link slots to booking
        for slot in slots:
            link = BookingSlot(booking_id=booking.id, slot_id=slot.id)
            self._db.add(link)
        self._db.flush()

        # FR-021: trigger email notification to instructor
        instructor_user = self._db.query(User).filter(User.id == instructor_id).first()
        if instructor_user and self._notification_service:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.NEW_PENDING_BOOKING,
                    subject="Nova reserva pendente",
                    body=f"Você tem um novo agendamento pendente criado pelo aluno {student_id}.",
                    recipients=[instructor_user.email],
                )
            )

        return booking

    def confirm_booking(self, booking_id: str, instructor_id: str) -> Booking:
        booking = self._get_booking_or_raise(booking_id)
        if booking.instructor_id != instructor_id:
            raise ValueError("Only the instructor can confirm this booking")

        new_status = transition_booking(
            BookingStatus(booking.status), BookingStatus.CONFIRMADA
        )
        booking.status = new_status.value
        booking.confirmed_at = datetime.now(timezone.utc)
        self._db.flush()

        # FR-021: trigger email notification to student
        student_user = self._db.query(User).filter(User.id == booking.student_id).first()
        if student_user and self._notification_service:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.BOOKING_CONFIRMED,
                    subject="Sua aula foi confirmada",
                    body=f"Sua solicitação de agendamento {booking_id} foi confirmada pelo instrutor {instructor_id}.",
                    recipients=[student_user.email],
                )
            )

        return booking

    def cancel_booking(
        self,
        booking_id: str,
        user_id: str,
        cancelled_by: str,
        reason: str | None = None,
    ) -> Booking:
        booking = self._get_booking_or_raise(booking_id)

        new_status = transition_booking(
            BookingStatus(booking.status), BookingStatus.CANCELADA
        )
        now = datetime.now(timezone.utc)

        booking.status = new_status.value
        booking.cancelled_at = now
        booking.cancelled_by = cancelled_by
        booking.cancellation_reason = reason

        # Release reserved slots back to DISPONIVEL
        for link in booking.slots:
            slot = self._db.query(Slot).filter(Slot.id == link.slot_id).first()
            if slot and slot.status == SlotStatus.RESERVADO.value:
                slot.status = SlotStatus.DISPONIVEL.value

        # RN04: penalty if student cancels within 24h of first slot
        if cancelled_by == CancelledBy.ALUNO.value:
            first_slot = (
                self._db.query(Slot)
                .join(BookingSlot, BookingSlot.slot_id == Slot.id)
                .filter(BookingSlot.booking_id == booking_id)
                .order_by(Slot.starts_at)
                .first()
            )
            if first_slot:
                time_until_slot = first_slot.starts_at - now
                if time_until_slot < timedelta(hours=CANCELLATION_NOTICE_HOURS):
                    self._penalty.apply_penalty(
                        booking.student_id,
                        reason=f"Cancelamento tardio (< 24h) do booking {booking_id} conforme RN04",
                    )

        self._db.flush()

        # FR-021: trigger email notification to student and/or instructor
        recipients = []
        if cancelled_by == CancelledBy.ALUNO.value:
            instructor_user = self._db.query(User).filter(User.id == booking.instructor_id).first()
            if instructor_user:
                recipients.append(instructor_user.email)
        elif cancelled_by == CancelledBy.INSTRUTOR.value:
            student_user = self._db.query(User).filter(User.id == booking.student_id).first()
            if student_user:
                recipients.append(student_user.email)
        else: # SISTEMA (timeouts)
            student_user = self._db.query(User).filter(User.id == booking.student_id).first()
            instructor_user = self._db.query(User).filter(User.id == booking.instructor_id).first()
            if student_user:
                recipients.append(student_user.email)
            if instructor_user:
                recipients.append(instructor_user.email)

        if recipients and self._notification_service:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.BOOKING_CANCELLED,
                    subject="Sua aula foi cancelada",
                    body=f"O agendamento {booking_id} foi cancelado por {cancelled_by}. Motivo: {reason or ''}",
                    recipients=recipients,
                )
            )

        return booking

    def get_booking(self, booking_id: str) -> Booking | None:
        return self._db.query(Booking).filter(Booking.id == booking_id).first()

    def list_bookings(
        self,
        user_id: str,
        role: str,
        status_filter: str | None = None,
    ) -> list[Booking]:
        if role == "ALUNO":
            query = self._db.query(Booking).filter(Booking.student_id == user_id)
        else:
            query = self._db.query(Booking).filter(Booking.instructor_id == user_id)

        if status_filter:
            query = query.filter(Booking.status == status_filter)

        return query.order_by(Booking.created_at.desc()).all()

    def _get_booking_or_raise(self, booking_id: str) -> Booking:
        booking = self.get_booking(booking_id)
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        return booking
