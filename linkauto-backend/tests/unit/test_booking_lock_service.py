import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.booking_lock_service import SqlAlchemySlotReservationStore


def test_sqlalchemy_slot_reservation_store_has_static_table_name():
    """
    D08 - P2: SqlAlchemySlotReservationStore deve possuir _TABLE_NAME estático como slots
    e não deve aceitar o parâmetro table_name no construtor.
    """
    # 1. Verifica se existe o atributo de classe privado _TABLE_NAME
    assert getattr(SqlAlchemySlotReservationStore, "_TABLE_NAME", None) == "slots"
    
    # 2. Verifica que tentar instanciar passando table_name levanta TypeError (pois o parâmetro foi removido)
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    with pytest.raises(TypeError):
        # Essa chamada deve falhar na fase GREEN quando o construtor for ajustado.
        # Na fase RED ela não vai levantar erro se o construtor aceitar **kwargs ou table_name.
        SqlAlchemySlotReservationStore(session, table_name="custom_table")
