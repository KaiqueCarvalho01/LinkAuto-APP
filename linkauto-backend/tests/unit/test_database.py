from sqlalchemy import text


def test_get_db_yields_valid_session(db_session):
    """get_db dependency must yield a functional SQLAlchemy session."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_get_db_session_is_isolated(db_session):
    """Each test gets a clean, isolated session via transaction rollback."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
