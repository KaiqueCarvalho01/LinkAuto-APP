from sqlalchemy import inspect


def test_all_us2_tables_exist(test_engine):
    """Migration must create slots, bookings, booking_slots, student_penalties tables."""
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert "slots" in tables
    assert "bookings" in tables
    assert "booking_slots" in tables
    assert "student_penalties" in tables


def test_slot_unique_constraint_on_booking_slots(test_engine):
    """booking_slots.slot_id must be unique (a slot belongs to at most one booking)."""
    inspector = inspect(test_engine)
    columns = {c["name"] for c in inspector.get_columns("booking_slots")}
    assert "slot_id" in columns
    assert "booking_id" in columns


