from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import hash_password
from app.models import (
    Base,
    Booking,
    BookingSlot,
    CancelledBy,
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


def seed_dev_data(session: Session) -> None:
    # 1. Admin user
    admin_user = session.query(User).filter_by(email="admin@linkauto.com.br").first()
    if not admin_user:
        admin_user = User(
            email="admin@linkauto.com.br",
            password_hash=hash_password("password123"),
            roles=[UserRole.ADMIN.value],
            is_active=True,
        )
        session.add(admin_user)
        session.flush()

    # 2. Student user
    student_user = session.query(User).filter_by(email="aluno@linkauto.com.br").first()
    if not student_user:
        student_user = User(
            email="aluno@linkauto.com.br",
            password_hash=hash_password("password123"),
            roles=[UserRole.ALUNO.value],
            is_active=True,
        )
        session.add(student_user)
        session.flush()

        student_profile = StudentProfile(
            user_id=student_user.id,
            full_name="Gabriel Silva",
            phone="19999998888",
            city="Mogi Mirim",
            state="SP",
            license_type=LicenseType.EM_PROCESSO,
        )
        session.add(student_profile)

    # 3. Instructor 1: Camila Rocha
    inst1_user = session.query(User).filter_by(email="camila@linkauto.com.br").first()
    if not inst1_user:
        inst1_user = User(
            email="camila@linkauto.com.br",
            password_hash=hash_password("password123"),
            roles=[UserRole.INSTRUTOR.value],
            is_active=True,
        )
        session.add(inst1_user)
        session.flush()

        inst1_profile = InstructorProfile(
            user_id=inst1_user.id,
            full_name="Camila Rocha",
            phone="19999997777",
            city="Mogi Mirim",
            state="SP",
            bio="Instrutora credenciada pelo DETRAN focada em alunos com medo de dirigir e recém-habilitados. Aulas práticas com paciência e didática moderna.",
            specialties=["Carro", "Medo de Dirigir"],
            price_per_hour=Decimal("70.00"),
            detran_status=DetranStatus.APROVADO,
            action_radius_km=15,
            latitude=-22.4319,
            longitude=-46.9578,
            rating_avg=4.8,
            rating_count=5,
            is_active=True,
        )
        session.add(inst1_profile)

    # 4. Instructor 2: Rafael Mendes
    inst2_user = session.query(User).filter_by(email="rafael@linkauto.com.br").first()
    if not inst2_user:
        inst2_user = User(
            email="rafael@linkauto.com.br",
            password_hash=hash_password("password123"),
            roles=[UserRole.INSTRUTOR.value],
            is_active=True,
        )
        session.add(inst2_user)
        session.flush()

        inst2_profile = InstructorProfile(
            user_id=inst2_user.id,
            full_name="Rafael Mendes",
            phone="19999996666",
            city="Mogi Guaçu",
            state="SP",
            bio="Especialista em categorias A e B. Foco em direção defensiva e preparação completa para exame prático do DETRAN.",
            specialties=["Carro", "Moto"],
            price_per_hour=Decimal("65.00"),
            detran_status=DetranStatus.APROVADO,
            action_radius_km=10,
            latitude=-22.3708,
            longitude=-46.9428,
            rating_avg=4.5,
            rating_count=2,
            is_active=True,
        )
        session.add(inst2_profile)

    # 5. Instructor 3: Fernanda Siqueira
    inst3_user = session.query(User).filter_by(email="fernanda@linkauto.com.br").first()
    if not inst3_user:
        inst3_user = User(
            email="fernanda@linkauto.com.br",
            password_hash=hash_password("password123"),
            roles=[UserRole.INSTRUTOR.value],
            is_active=True,
        )
        session.add(inst3_user)
        session.flush()

        inst3_profile = InstructorProfile(
            user_id=inst3_user.id,
            full_name="Fernanda Siqueira",
            phone="19999995555",
            city="Estiva Gerbi",
            state="SP",
            bio="Habilitada para aulas práticas PCD com veículo adaptado. Didática inclusiva e focada na autonomia do condutor.",
            specialties=["Habilitação PCD"],
            price_per_hour=Decimal("80.00"),
            detran_status=DetranStatus.APROVADO,
            action_radius_km=20,
            latitude=-22.2842,
            longitude=-46.9692,
            rating_avg=5.0,
            rating_count=1,
            is_active=True,
        )
        session.add(inst3_profile)

    session.flush()

    # Get IDs
    student_id = student_user.id
    inst1_id = inst1_user.id
    inst2_id = inst2_user.id
    inst3_id = inst3_user.id

    # Check if slots already exist
    existing_slots = session.query(Slot).filter_by(instructor_id=inst1_id).first()
    if not existing_slots:
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

        # Generate slots for next 5 days
        for day in range(5):
            base_date = now + timedelta(days=day)
            
            # Camila Rocha (inst1)
            for hour in [8, 9, 10, 11, 14, 15, 16]:
                start = base_date.replace(hour=hour)
                end = start + timedelta(hours=1)
                if start <= datetime.now(timezone.utc):
                    continue
                slot = Slot(
                    instructor_id=inst1_id,
                    starts_at=start,
                    ends_at=end,
                    status=SlotStatus.DISPONIVEL.value,
                )
                session.add(slot)

            # Rafael Mendes (inst2)
            for hour in [9, 10, 11, 13, 14, 15]:
                start = base_date.replace(hour=hour)
                end = start + timedelta(hours=1)
                if start <= datetime.now(timezone.utc):
                    continue
                slot = Slot(
                    instructor_id=inst2_id,
                    starts_at=start,
                    ends_at=end,
                    status=SlotStatus.DISPONIVEL.value,
                )
                session.add(slot)

            # Fernanda Siqueira (inst3)
            for hour in [10, 11, 14, 15, 16, 17]:
                start = base_date.replace(hour=hour)
                end = start + timedelta(hours=1)
                if start <= datetime.now(timezone.utc):
                    continue
                slot = Slot(
                    instructor_id=inst3_id,
                    starts_at=start,
                    ends_at=end,
                    status=SlotStatus.DISPONIVEL.value,
                )
                session.add(slot)

        session.flush()

        # Create a PENDING booking with Rafael Mendes (inst2) for tomorrow
        tomorrow = now + timedelta(days=1)
        slots_inst2 = session.query(Slot).filter(
            Slot.instructor_id == inst2_id,
            Slot.starts_at >= tomorrow.replace(hour=9),
            Slot.starts_at <= tomorrow.replace(hour=12),
        ).all()

        if len(slots_inst2) >= 2:
            slots_inst2[0].status = SlotStatus.RESERVADO.value
            slots_inst2[1].status = SlotStatus.RESERVADO.value

            booking = Booking(
                student_id=student_id,
                instructor_id=inst2_id,
                status="PENDENTE",
                location_description="Próximo à Rodoviária de Mogi Guaçu",
                latitude=-22.3712,
                longitude=-46.9430,
            )
            session.add(booking)
            session.flush()

            bs1 = BookingSlot(booking_id=booking.id, slot_id=slots_inst2[0].id)
            bs2 = BookingSlot(booking_id=booking.id, slot_id=slots_inst2[1].id)
            session.add(bs1)
            session.add(bs2)

        # Create a REALIZADA booking with Fernanda Siqueira (inst3) in the past with review
        yesterday = now - timedelta(days=1)
        slot_past1 = Slot(
            instructor_id=inst3_id,
            starts_at=yesterday.replace(hour=10),
            ends_at=yesterday.replace(hour=11),
            status=SlotStatus.RESERVADO.value,
        )
        slot_past2 = Slot(
            instructor_id=inst3_id,
            starts_at=yesterday.replace(hour=11),
            ends_at=yesterday.replace(hour=12),
            status=SlotStatus.RESERVADO.value,
        )
        session.add(slot_past1)
        session.add(slot_past2)
        session.flush()

        past_booking = Booking(
            student_id=student_id,
            instructor_id=inst3_id,
            status="REALIZADA",
            location_description="Centro de Estiva Gerbi",
            latitude=-22.2845,
            longitude=-46.9695,
        )
        session.add(past_booking)
        session.flush()

        bs_past1 = BookingSlot(booking_id=past_booking.id, slot_id=slot_past1.id)
        bs_past2 = BookingSlot(booking_id=past_booking.id, slot_id=slot_past2.id)
        session.add(bs_past1)
        session.add(bs_past2)
        session.flush()

        review = Review(
            booking_id=past_booking.id,
            reviewer_id=student_id,
            reviewed_id=inst3_id,
            rating=5,
            comment="Fernanda é excelente! Muito paciente e didática. O carro adaptado para PCD é ótimo.",
        )
        session.add(review)

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
