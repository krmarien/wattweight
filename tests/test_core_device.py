"""Unit tests for the DeviceManager."""

import pytest
from typing import Generator

from wattweight.database import Database
from wattweight.core.device import DeviceManager, DeviceAlreadyExistsError, DeviceNotFoundError
from wattweight.model.device import Device


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


def test_add_device(device_manager: DeviceManager):
    """Test adding a new device."""
    device = device_manager.add_device(
        identifier="test-device",
        name="Test Device",
        description="A test device",
    )
    assert device.identifier == "test-device"
    assert device.name == "Test Device"
    assert device.description == "A test device"


def test_add_device_already_exists(device_manager: DeviceManager):
    """Test adding a device that already exists."""
    device_manager.add_device(identifier="test-device", name="Test Device")
    with pytest.raises(DeviceAlreadyExistsError):
        device_manager.add_device(identifier="test-device", name="Another Device")


def test_get_all_devices(device_manager: DeviceManager):
    """Test getting all devices."""
    device_manager.add_device(identifier="dev1", name="Device 1")
    device_manager.add_device(identifier="dev2", name="Device 2")
    
    devices = device_manager.get_all_devices()
    assert len(devices) == 2


def test_get_device_by_identifier(device_manager: DeviceManager):
    """Test getting a device by its identifier."""
    device_manager.add_device(identifier="test-device", name="Test Device")
    
    device = device_manager.get_device_by_identifier("test-device")
    assert device is not None
    assert device.name == "Test Device"


def test_get_device_by_identifier_not_found(device_manager: DeviceManager):
    """Test getting a device that does not exist."""
    with pytest.raises(DeviceNotFoundError):
        device_manager.get_device_by_identifier("non-existent-device")


def test_update_device(device_manager: DeviceManager):
    """Test updating a device."""
    device = device_manager.add_device(identifier="test-device", name="Test Device")
    
    updated_device = device_manager.update_device(
        identifier="test-device",
        name="Updated Name",
        description="Updated Description"
    )
    
    assert updated_device.name == "Updated Name"
    assert updated_device.description == "Updated Description"


def test_update_device_not_found(device_manager: DeviceManager):
    """Test updating a device that does not exist."""
    with pytest.raises(DeviceNotFoundError):
        device_manager.update_device(identifier="non-existent-device", name="New Name")


def test_update_device_no_fields(device_manager: DeviceManager):
    """Test updating a device with no fields."""
    device_manager.add_device(identifier="test-device", name="Test Device")
    with pytest.raises(ValueError):
        device_manager.update_device(identifier="test-device")


def test_update_device_idle_timeout(device_manager: DeviceManager):
    """Test updating only the idle_timeout of a device."""
    device_manager.add_device(identifier="test-device", name="Test Device", idle_timeout=100)
    updated_device = device_manager.update_device(identifier="test-device", idle_timeout=200)
    assert updated_device.idle_timeout == 200


def test_update_device_idle_power(device_manager: DeviceManager):
    """Test updating only the idle_power of a device."""
    device_manager.add_device(identifier="test-device", name="Test Device", idle_power=5.0)
    updated_device = device_manager.update_device(identifier="test-device", idle_power=10.0)
    assert updated_device.idle_power == 10.0


def test_delete_device(device_manager: DeviceManager):
    """Test deleting a device."""
    device = device_manager.add_device(identifier="test-device", name="Test Device")
    
    device_manager.delete_device("test-device")
    
    with pytest.raises(DeviceNotFoundError):
        device_manager.get_device_by_identifier("test-device")


def test_delete_device_not_found(device_manager: DeviceManager):
    """Test deleting a device that does not exist."""
    with pytest.raises(DeviceNotFoundError):
        device_manager.delete_device("non-existent-device")
