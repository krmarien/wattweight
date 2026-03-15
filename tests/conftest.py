import pytest
from sqlmodel import create_engine, Session, SQLModel

from wattweight.core.base import Core
from wattweight.database import Database


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        Core._db = session
        yield session
    Core._db = None


@pytest.fixture(autouse=True, scope="function")
def setup_per_function():
    db = Database(in_memory=True)
    db.init_db()
    yield
    db.close()
