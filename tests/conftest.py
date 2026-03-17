import pytest

from wattweight.database import Database


@pytest.fixture(autouse=True, scope="function")
def setup_and_teardown_db():
    with Database(in_memory=True):
        yield
