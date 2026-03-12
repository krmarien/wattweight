"""Unit tests for the BaseManager."""

import pytest
from typing import Generator
from unittest.mock import MagicMock

from wattweight.database import Database
from wattweight.core.base import BaseManager
from wattweight.core.device import DeviceManager


@pytest.fixture
def db() -> Generator[Database, None, None]:
    """Fixture for an in-memory database."""
    database = Database(db_dir=None)
    with database as db_conn:
        yield db_conn


@pytest.fixture
def device_manager(db: Database) -> DeviceManager:
    """Fixture for the DeviceManager."""
    return DeviceManager(db)


def test_base_manager_as_context_manager(device_manager: DeviceManager):
    """Test using the BaseManager as a context manager."""
    assert BaseManager._session is None
    assert BaseManager._session_owner is None

    with device_manager as dm:
        assert BaseManager._session is not None
        assert BaseManager._session_owner == dm.__class__
        # Check that it's the same manager instance
        assert dm is device_manager

    assert BaseManager._session is None
    assert BaseManager._session_owner is None


def test_nested_context_managers(db: Database):
    """Test nested context managers."""
    dm1 = DeviceManager(db)
    dm2 = DeviceManager(db)

    assert BaseManager._session is None
    assert BaseManager._session_owner is None

    with dm1:
        assert BaseManager._session is not None
        assert BaseManager._session_owner == dm1.__class__
        session1 = BaseManager._session
        dm1._get_session() == session1

        with dm2:
            assert BaseManager._session is not None
            # The session owner should still be the first manager
            assert BaseManager._session_owner == dm1.__class__
            session2 = BaseManager._session
            assert session1 is session2

        # Exiting the inner context manager should not close the session
        assert BaseManager._session is not None
        assert BaseManager._session_owner == dm1.__class__

    assert BaseManager._session is None
    assert BaseManager._session_owner is None


def test_set_session():
    """Test the set_session method."""
    mock_session = MagicMock()

    assert BaseManager._session is None

    BaseManager.set_session(mock_session)
    assert BaseManager._session is mock_session

    BaseManager.set_session(None)
    assert BaseManager._session is None
    assert BaseManager._session_owner is None


def test_get_session_without_context(device_manager: DeviceManager):
    """Test the _get_session method without a context manager."""
    assert BaseManager._session is None
    devices = device_manager.get_all_devices()
    assert isinstance(devices, list)
