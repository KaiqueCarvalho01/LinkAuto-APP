from __future__ import annotations

from enum import Enum


class BookingStatus(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADA = "CONFIRMADA"
    REALIZADA = "REALIZADA"
    CANCELADA = "CANCELADA"


TERMINAL_STATUSES = {BookingStatus.REALIZADA, BookingStatus.CANCELADA}

ALLOWED_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
    BookingStatus.PENDENTE: {BookingStatus.CONFIRMADA, BookingStatus.CANCELADA},
    BookingStatus.CONFIRMADA: {BookingStatus.REALIZADA, BookingStatus.CANCELADA},
    BookingStatus.REALIZADA: set(),
    BookingStatus.CANCELADA: set(),
}


class BookingTransitionError(ValueError):
    pass


def can_transition(
    current: BookingStatus, target: BookingStatus, *, admin_override: bool = False
) -> bool:
    if current == target:
        return True
    if admin_override and current in TERMINAL_STATUSES and target in TERMINAL_STATUSES:
        return True
    return target in ALLOWED_TRANSITIONS[current]


def ensure_transition_allowed(
    current: BookingStatus, target: BookingStatus, *, admin_override: bool = False
) -> None:
    if not can_transition(current, target, admin_override=admin_override):
        raise BookingTransitionError(
            f"Invalid booking transition: {current.value} -> {target.value}"
        )


def transition_booking(
    current: BookingStatus, target: BookingStatus, *, admin_override: bool = False
) -> BookingStatus:
    ensure_transition_allowed(current, target, admin_override=admin_override)
    return target
