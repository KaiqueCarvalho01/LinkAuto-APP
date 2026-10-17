"""Run the scheduled jobs against the configured database, without HTTP or an admin token.

Usage: ``python -m app.jobs run <job>... | all``. Schedule it once per environment (cron,
Kubernetes CronJob, platform scheduler or the compose ``scheduler`` service), not in every
replica; every 15 minutes is enough. Running it twice, even concurrently, is safe.

Prints one JSON summary line per job and exits with status 1 when a booking failed.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from typing import TYPE_CHECKING

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.jobs.runner import Job, run_job
from app.services.dependencies import get_notification_service

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger("app.jobs")

ALL = "all"


def _parse(argv: Sequence[str] | None) -> list[Job]:
    parser = argparse.ArgumentParser(prog="python -m app.jobs", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run jobs once and exit")
    run.add_argument("jobs", nargs="+", choices=[*Job, ALL], metavar="JOB")
    args = parser.parse_args(argv)
    if ALL in args.jobs:
        return list(Job)
    return [Job(name) for name in dict.fromkeys(args.jobs)]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested jobs, each in its own transaction; return the exit status."""
    setup_logging()
    notifications = get_notification_service()
    failed = False
    for job in _parse(argv):
        with SessionLocal() as db:
            try:
                result = run_job(job, db, notifications)
                db.commit()
            except Exception:
                db.rollback()
                logger.exception("Job %s failed", job.value, extra={"event": "jobs.run.error"})
                failed = True
                continue
        failed = failed or result.failed > 0
        print(json.dumps({"job": job.value, **asdict(result)}))  # noqa: T201 - CLI output
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
