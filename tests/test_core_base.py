from sqlmodel import Session

from wattweight.core.base import Core


def test_core_db_property():
    """Test the db property of the Core class."""
    # Reset class-level database session for isolated test
    Core._db = None

    core1 = Core()
    core2 = Core()

    # First access should create a session
    session1 = core1.db
    assert session1 is not None
    assert isinstance(session1, Session)

    # Second access on same instance should return same session
    session2 = core1.db
    assert session1 is session2

    # Access from another instance should also return the same session
    session3 = core2.db
    assert session1 is session3

    # Reset for other tests
    Core._db = None
