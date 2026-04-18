import pytest

from app.domain.booking import BookingStatus, BookingTransitionError, can_transition, transition_booking


def test_allows_valid_transitions():
    assert transition_booking(BookingStatus.PENDENTE, BookingStatus.CONFIRMADA) == BookingStatus.CONFIRMADA
    assert transition_booking(BookingStatus.PENDENTE, BookingStatus.CANCELADA) == BookingStatus.CANCELADA
    assert transition_booking(BookingStatus.CONFIRMADA, BookingStatus.CANCELADA) == BookingStatus.CANCELADA
    assert transition_booking(BookingStatus.CONFIRMADA, BookingStatus.REALIZADA) == BookingStatus.REALIZADA


def test_blocks_invalid_transition_from_pending_to_realizada():
    with pytest.raises(BookingTransitionError):
        transition_booking(BookingStatus.PENDENTE, BookingStatus.REALIZADA)


def test_blocks_invalid_transition_from_terminal_without_admin_override():
    with pytest.raises(BookingTransitionError):
        transition_booking(BookingStatus.CANCELADA, BookingStatus.REALIZADA)


def test_allows_terminal_admin_override_for_operational_correction():
    assert can_transition(
        BookingStatus.CANCELADA,
        BookingStatus.REALIZADA,
        admin_override=True,
    )
    assert (
        transition_booking(
            BookingStatus.CANCELADA,
            BookingStatus.REALIZADA,
            admin_override=True,
        )
        == BookingStatus.REALIZADA
    )
