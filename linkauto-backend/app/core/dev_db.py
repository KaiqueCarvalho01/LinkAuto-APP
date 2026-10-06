from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.domain.booking import MIN_SLOTS_PER_BOOKING
from app.models import (
    Base,
    Booking,
    BookingSlot,
    DetranStatus,
    InstructorProfile,
    LicenseType,
    Review,
    Slot,
    SlotStatus,
    StudentProfile,
    User,
    UserRole,
)

if TYPE_CHECKING:
    from app.core.config import Settings


def _sqlite_file_from_url(database_url: str) -> Path | None:
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite"):
        return None

    database = url.database
    if not database or database == ":memory:":
        return None

    sqlite_path = Path(database)
    if not sqlite_path.is_absolute():
        sqlite_path = Path.cwd() / sqlite_path

    return sqlite_path


DEV_PASSWORD = "password123"  # noqa: S105 - well-known credentials for local development only

STUDENT_SLUG = "gabriel-silva-mogi-mirim-1a2b"

# (email, profile fields, daily slot hours)
DEV_INSTRUCTORS: list[tuple[str, dict[str, Any], list[int]]] = [
    (
        "camila@linkauto.com.br",
        {
            "slug": "camila-rocha-mogi-mirim-8f2a",
            "full_name": "Camila Rocha",
            "phone": "19999997777",
            "city": "Mogi Mirim",
            "bio": (
                "Instrutora credenciada pelo DETRAN focada em alunos com medo de dirigir e "
                "recém-habilitados. Aulas práticas com paciência e didática moderna."
            ),
            "specialties": ["Carro", "Medo de Dirigir"],
            "price_per_hour": Decimal("70.00"),
            "action_radius_km": 15,
            "latitude": -22.4319,
            "longitude": -46.9578,
            "rating_avg": 4.8,
            "rating_count": 5,
        },
        [8, 9, 10, 11, 14, 15, 16],
    ),
    (
        "rafael@linkauto.com.br",
        {
            "slug": "rafael-mendes-mogi-guacu-3c1d",
            "full_name": "Rafael Mendes",
            "phone": "19999996666",
            "city": "Mogi Guaçu",
            "bio": (
                "Especialista em categorias A e B. Foco em direção defensiva e preparação "
                "completa para exame prático do DETRAN."
            ),
            "specialties": ["Carro", "Moto"],
            "price_per_hour": Decimal("65.00"),
            "action_radius_km": 10,
            "latitude": -22.3708,
            "longitude": -46.9428,
            "rating_avg": 4.5,
            "rating_count": 2,
        },
        [9, 10, 11, 13, 14, 15],
    ),
    (
        "fernanda@linkauto.com.br",
        {
            "slug": "fernanda-siqueira-estiva-gerbi-9e4b",
            "full_name": "Fernanda Siqueira",
            "phone": "19999995555",
            "city": "Estiva Gerbi",
            "bio": (
                "Habilitada para aulas práticas PCD com veículo adaptado. Didática inclusiva e "
                "focada na autonomia do condutor."
            ),
            "specialties": ["Habilitação PCD"],
            "price_per_hour": Decimal("80.00"),
            "action_radius_km": 20,
            "latitude": -22.2842,
            "longitude": -46.9692,
            "rating_avg": 5.0,
            "rating_count": 1,
        },
        [10, 11, 14, 15, 16, 17],
    ),
]

SLOT_DAYS = 5


def _upsert_user(session: Session, email: str, role: UserRole) -> tuple[User, bool]:
    """Return the dev user with this email, creating it if needed (and whether it was created)."""
    user = session.query(User).filter_by(email=email).first()
    if user:
        return user, False
    user = User(
        email=email, password_hash=hash_password(DEV_PASSWORD), roles=[role.value], is_active=True
    )
    session.add(user)
    session.flush()
    return user, True


def _reset_credentials(user: User, role: UserRole) -> None:
    # Keep credentials and roles synchronized in dev
    user.password_hash = hash_password(DEV_PASSWORD)
    user.roles = [role.value]
    user.is_active = True


def _seed_admin(session: Session) -> None:
    admin, created = _upsert_user(session, "admin@linkauto.com.br", UserRole.ADMIN)
    if not created:
        _reset_credentials(admin, UserRole.ADMIN)
    session.flush()


def _seed_student(session: Session) -> User:
    student, created = _upsert_user(session, "aluno@linkauto.com.br", UserRole.ALUNO)
    if created:
        session.add(
            StudentProfile(
                user_id=student.id,
                slug=STUDENT_SLUG,
                full_name="Gabriel Silva",
                phone="19999998888",
                city="Mogi Mirim",
                state="SP",
                license_type=LicenseType.EM_PROCESSO,
            )
        )
    else:
        _reset_credentials(student, UserRole.ALUNO)
        if student.student_profile and not student.student_profile.slug:
            student.student_profile.slug = STUDENT_SLUG
    return student


def _seed_instructor(session: Session, email: str, profile: dict[str, Any]) -> User:
    instructor, created = _upsert_user(session, email, UserRole.INSTRUTOR)
    if created:
        session.add(
            InstructorProfile(
                user_id=instructor.id,
                state="SP",
                detran_status=DetranStatus.APROVADO,
                is_active=True,
                **profile,
            )
        )
    elif instructor.instructor_profile and not instructor.instructor_profile.slug:
        instructor.instructor_profile.slug = profile["slug"]
    return instructor


def _add_slots(session: Session, instructor_id: str, now: datetime, hours: list[int]) -> None:
    for day in range(SLOT_DAYS):
        base_date = now + timedelta(days=day)
        for hour in hours:
            start = base_date.replace(hour=hour)
            if start <= datetime.now(UTC):
                continue
            session.add(
                Slot(
                    instructor_id=instructor_id,
                    starts_at=start,
                    ends_at=start + timedelta(hours=1),
                    status=SlotStatus.DISPONIVEL.value,
                )
            )


def _add_booking(session: Session, slots: list[Slot], booking: Booking) -> Booking:
    for slot in slots:
        slot.status = SlotStatus.RESERVADO.value
    session.add(booking)
    session.flush()
    session.add_all(BookingSlot(booking_id=booking.id, slot_id=slot.id) for slot in slots)
    return booking


def _seed_pending_booking(
    session: Session, student_id: str, instructor_id: str, now: datetime
) -> None:
    """Create a PENDENTE booking for tomorrow morning."""
    tomorrow = now + timedelta(days=1)
    slots = (
        session.query(Slot)
        .filter(
            Slot.instructor_id == instructor_id,
            Slot.starts_at >= tomorrow.replace(hour=9),
            Slot.starts_at <= tomorrow.replace(hour=12),
        )
        .all()
    )
    if len(slots) < MIN_SLOTS_PER_BOOKING:
        return
    _add_booking(
        session,
        slots[:MIN_SLOTS_PER_BOOKING],
        Booking(
            student_id=student_id,
            instructor_id=instructor_id,
            status="PENDENTE",
            location_description="Próximo à Rodoviária de Mogi Guaçu",
            latitude=-22.3712,
            longitude=-46.9430,
        ),
    )


def _seed_completed_booking_with_review(
    session: Session, student_id: str, instructor_id: str, now: datetime
) -> None:
    """Create a REALIZADA booking from yesterday, reviewed by the student."""
    yesterday = now - timedelta(days=1)
    slots = [
        Slot(
            instructor_id=instructor_id,
            starts_at=yesterday.replace(hour=hour),
            ends_at=yesterday.replace(hour=hour + 1),
            status=SlotStatus.RESERVADO.value,
        )
        for hour in (10, 11)
    ]
    session.add_all(slots)
    session.flush()
    booking = _add_booking(
        session,
        slots,
        Booking(
            student_id=student_id,
            instructor_id=instructor_id,
            status="REALIZADA",
            location_description="Centro de Estiva Gerbi",
            latitude=-22.2845,
            longitude=-46.9695,
        ),
    )
    session.flush()
    session.add(
        Review(
            booking_id=booking.id,
            reviewer_id=student_id,
            reviewed_id=instructor_id,
            rating=5,
            comment=(
                "Fernanda é excelente! Muito paciente e didática. O carro adaptado para PCD é "
                "ótimo."
            ),
        )
    )


def seed_dev_data(session: Session) -> None:
    """Seed (idempotently) demo users, instructors, slots, bookings and a review."""
    _seed_admin(session)
    student = _seed_student(session)
    instructors = [
        (_seed_instructor(session, email, profile), hours)
        for email, profile, hours in DEV_INSTRUCTORS
    ]
    session.flush()

    camila, rafael, fernanda = (instructor for instructor, _ in instructors)
    if not session.query(Slot).filter_by(instructor_id=camila.id).first():
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        for instructor, hours in instructors:
            _add_slots(session, instructor.id, now, hours)
        session.flush()
        _seed_pending_booking(session, student.id, rafael.id, now)
        _seed_completed_booking_with_review(session, student.id, fernanda.id, now)

    session.commit()


def initialize_sqlite_dev_database(settings: Settings) -> None:
    if settings.app_env.lower() != "development":
        return

    sqlite_file = _sqlite_file_from_url(settings.database_url)
    if sqlite_file is None:
        return

    sqlite_file.parent.mkdir(parents=True, exist_ok=True)

    if settings.reset_sqlite_on_startup and sqlite_file.exists():
        sqlite_file.unlink()

    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    try:
        Base.metadata.create_all(bind=engine)
        if settings.reset_sqlite_on_startup:
            with Session(engine) as session:
                seed_dev_data(session)
    finally:
        engine.dispose()
