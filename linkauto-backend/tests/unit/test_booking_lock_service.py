from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, InstructorProfile, Slot, SlotStatus, User
from app.services.booking_lock_service import SqlAlchemySlotReservationStore


def test_sqlalchemy_slot_reservation_store_has_static_table_name() -> None:
    """D08 - P2: SqlAlchemySlotReservationStore deve possuir _TABLE_NAME estático.

    O valor deve ser "slots", e o construtor não deve aceitar o parâmetro table_name.
    """
    # 1. Verifica se existe o atributo de classe privado _TABLE_NAME
    assert getattr(SqlAlchemySlotReservationStore, "_TABLE_NAME", None) == "slots"

    # 2. Verifica que tentar instanciar passando table_name levanta TypeError
    # (pois o parâmetro foi removido)
    engine = create_engine("sqlite:///:memory:")
    session = sessionmaker(bind=engine)()

    with pytest.raises(TypeError):
        # Essa chamada deve falhar na fase GREEN quando o construtor for ajustado.
        # Na fase RED ela não vai levantar erro se o construtor aceitar **kwargs ou table_name.
        SqlAlchemySlotReservationStore(session, table_name="custom_table")  # ty: ignore[unknown-argument]


def test_sqlalchemy_slot_reservation_store_reserves_all_or_nothing() -> None:

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    user = User(email="lock@test.com", password_hash="x", roles=["INSTRUTOR"])
    session.add(user)
    session.flush()
    session.add(InstructorProfile(user_id=user.id))
    start = datetime(2030, 1, 1, 9, tzinfo=UTC)
    slots = [
        Slot(
            instructor_id=user.id,
            starts_at=start + timedelta(hours=i),
            ends_at=start + timedelta(hours=i + 1),
        )
        for i in range(3)
    ]
    session.add_all(slots)
    session.commit()
    first, second, third = (slot.id for slot in slots)
    session.close()  # the store begins its own transaction

    store = SqlAlchemySlotReservationStore(session)
    assert store.reserve_if_all_available([first, second]) is True
    # `second` is already reserved, so nothing is reserved
    assert store.reserve_if_all_available([second, third]) is False

    session.expire_all()
    statuses = {slot.id: slot.status for slot in session.query(Slot).all()}
    assert statuses == {
        first: SlotStatus.RESERVADO,
        second: SlotStatus.RESERVADO,
        third: SlotStatus.DISPONIVEL,
    }
