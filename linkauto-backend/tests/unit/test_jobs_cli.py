import json
from contextlib import nullcontext
from typing import TYPE_CHECKING

import pytest

from app.domain.booking import BookingStatus
from app.jobs import __main__ as cli
from app.models.booking import Booking
from app.services.notification_service import InMemoryEmailGateway, NotificationService
from tests.unit.test_booking_automation import _seed_full_booking

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlmodel import Session

type Summary = dict[str, object]
type RunCli = Callable[..., tuple[int, list[Summary]]]


@pytest.fixture
def run_cli(
    db_session: Session, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> RunCli:
    monkeypatch.setattr(cli, "SessionLocal", lambda: nullcontext(db_session))
    monkeypatch.setattr(
        cli, "get_notification_service", lambda: NotificationService(InMemoryEmailGateway())
    )

    def run(*argv: str) -> tuple[int, list[Summary]]:
        status = cli.main(list(argv))
        lines = capsys.readouterr().out.splitlines()
        return status, [json.loads(line) for line in lines]

    return run


def test_run_all_runs_every_job(run_cli: RunCli) -> None:
    status, summaries = run_cli("run", "all")

    assert status == 0
    assert [s["job"] for s in summaries] == ["timeout", "completion", "reminder", "token-cleanup"]
    assert summaries[-1] == {
        "job": "token-cleanup",
        "refresh_tokens_deleted": 0,
        "password_reset_tokens_deleted": 0,
        "failed": 0,
    }


def test_run_cancels_expired_pending_bookings(run_cli: RunCli, db_session: Session) -> None:
    booking = _seed_full_booking(db_session, BookingStatus.PENDENTE.value, starts_offset_hours=48)

    status, summaries = run_cli("run", "timeout")

    assert status == 0
    assert summaries == [
        {
            "job": "timeout",
            "processed": 1,
            "booking_ids": [booking.id],
            "failed": 0,
            "failed_booking_ids": [],
        }
    ]
    db_session.expire_all()
    stored = db_session.get(Booking, booking.id)
    assert stored is not None
    assert stored.status == BookingStatus.CANCELADA.value


def test_unknown_job_is_a_usage_error(run_cli: RunCli) -> None:
    with pytest.raises(SystemExit) as exc:
        run_cli("run", "nope")

    assert exc.value.code == 2
