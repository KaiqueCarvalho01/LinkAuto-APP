"""Booking statuses, RN02 slot minimum and the allowed status transitions."""

from __future__ import annotations

from enum import StrEnum


class BookingStatus(StrEnum):
    """Lifecycle status of a booking: PENDENTE -> CONFIRMADA -> REALIZADA, or CANCELADA."""

    PENDENTE = "PENDENTE"
    CONFIRMADA = "CONFIRMADA"
    REALIZADA = "REALIZADA"
    CANCELADA = "CANCELADA"


# RN02: a booking spans at least this many consecutive one-hour slots
MIN_SLOTS_PER_BOOKING = 2

TERMINAL_STATUSES = {BookingStatus.REALIZADA, BookingStatus.CANCELADA}

ALLOWED_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
    BookingStatus.PENDENTE: {BookingStatus.CONFIRMADA, BookingStatus.CANCELADA},
    BookingStatus.CONFIRMADA: {BookingStatus.REALIZADA, BookingStatus.CANCELADA},
    BookingStatus.REALIZADA: set(),
    BookingStatus.CANCELADA: set(),
}


class BookingTransitionError(ValueError):
    """Raised when a booking status change is not allowed by the state machine."""


def can_transition(
    current: BookingStatus, target: BookingStatus, *, admin_override: bool = False
) -> bool:
    """Return whether a booking may move from ``current`` to ``target``.

    Staying in the same status is always allowed. With ``admin_override``, an admin may
    also switch between the terminal statuses REALIZADA and CANCELADA.
    """
    if current == target:
        return True
    if admin_override and current in TERMINAL_STATUSES and target in TERMINAL_STATUSES:
        return True
    return target in ALLOWED_TRANSITIONS[current]


def ensure_transition_allowed(
    current: BookingStatus, target: BookingStatus, *, admin_override: bool = False
) -> None:
    """Raise ``BookingTransitionError`` if the transition is not allowed."""
    if not can_transition(current, target, admin_override=admin_override):
        msg = f"Invalid booking transition: {current.value} -> {target.value}"
        raise BookingTransitionError(msg)


def transition_booking(
    current: BookingStatus, target: BookingStatus, *, admin_override: bool = False
) -> BookingStatus:
    """Return ``target`` if the transition is allowed, else raise ``BookingTransitionError``."""
    ensure_transition_allowed(current, target, admin_override=admin_override)
    return target
