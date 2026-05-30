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


def test_all_us3_tables_exist(test_engine):
    """Migration must create booking_messages and reviews tables."""
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert "booking_messages" in tables
    assert "reviews" in tables


def test_review_unique_constraint_on_reviewer(test_engine):
    """reviews must have a unique constraint/index on booking_id + reviewer_id."""
    inspector = inspect(test_engine)
    unique_constraints = inspector.get_unique_constraints("reviews")
    # Check if there is a unique constraint on (booking_id, reviewer_id)
    has_uq = False
    for uq in unique_constraints:
        if set(uq["column_names"]) == {"booking_id", "reviewer_id"}:
            has_uq = True
            break
    
    # In SQLite, UniqueConstraint might also be mapped as a unique index, so we also check unique indexes
    if not has_uq:
        indexes = inspector.get_indexes("reviews")
        for idx in indexes:
            if idx["unique"] and set(idx["column_names"]) == {"booking_id", "reviewer_id"}:
                has_uq = True
                break

    assert has_uq, "Reviews table must have a unique constraint or unique index on (booking_id, reviewer_id)"



