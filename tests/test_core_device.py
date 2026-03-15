"""Unit tests for the DeviceCore."""

import pytest
from sqlmodel import Session

from wattweight.core.device import (
    DeviceCore,
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
)


def test_add_device(session: Session):
    """Test adding a new device."""
    device_core = DeviceCore()
    device = device_core.add_device(
        identifier="test-device",
        name="Test Device",
        description="A test device",
    )
    assert device.identifier == "test-device"
    assert device.name == "Test Device"
    assert device.description == "A test device"


def test_add_device_already_exists(session: Session):
    """Test adding a device that already exists."""
    device_core = DeviceCore()
    device_core.add_device(identifier="test-device", name="Test Device")
    with pytest.raises(DeviceAlreadyExistsError):
        device_core.add_device(identifier="test-device", name="Another Device")


def test_get_all_devices(session: Session):
    """Test getting all devices."""
    device_core = DeviceCore()
    device_core.add_device(identifier="dev1", name="Device 1")
    device_core.add_device(identifier="dev2", name="Device 2")

    devices = device_core.get_all_devices()
    assert len(devices) == 2


def test_get_device_by_identifier(session: Session):
    """Test getting a device by its identifier."""
    device_core = DeviceCore()
    device_core.add_device(identifier="test-device", name="Test Device")

    device = device_core.get_device_by_identifier("test-device")
    assert device is not None
    assert device.name == "Test Device"


def test_get_device_by_identifier_not_found(session: Session):
    """Test getting a device that does not exist."""
    device_core = DeviceCore()
    with pytest.raises(DeviceNotFoundError):
        device_core.get_device_by_identifier("non-existent-device")


def test_update_device(session: Session):
    """Test updating a device."""
    device_core = DeviceCore()
    _ = device_core.add_device(identifier="test-device", name="Test Device")

    updated_device = device_core.update_device(
        identifier="test-device", name="Updated Name", description="Updated Description"
    )

    assert updated_device.name == "Updated Name"
    assert updated_device.description == "Updated Description"


def test_update_device_not_found(session: Session):
    """Test updating a device that does not exist."""
    device_core = DeviceCore()
    with pytest.raises(DeviceNotFoundError):
        device_core.update_device(identifier="non-existent-device", name="New Name")


def test_update_device_no_fields(session: Session):
    """Test updating a device with no fields."""
    device_core = DeviceCore()
    device_core.add_device(identifier="test-device", name="Test Device")
    with pytest.raises(ValueError):
        device_core.update_device(identifier="test-device")


def test_update_device_idle_timeout(session: Session):
    """Test updating only the idle_timeout of a device."""
    device_core = DeviceCore()
    device_core.add_device(
        identifier="test-device", name="Test Device", idle_timeout=100
    )
    updated_device = device_core.update_device(
        identifier="test-device", idle_timeout=200
    )
    assert updated_device.idle_timeout == 200


def test_update_device_idle_power(session: Session):
    """Test updating only the idle_power of a device."""
    device_core = DeviceCore()
    device_core.add_device(identifier="test-device", name="Test Device", idle_power=5.0)
    updated_device = device_core.update_device(
        identifier="test-device", idle_power=10.0
    )
    assert updated_device.idle_power == 10.0


def test_delete_device(session: Session):
    """Test deleting a device."""
    device_core = DeviceCore()
    _ = device_core.add_device(identifier="test-device", name="Test Device")

    device_core.delete_device("test-device")

    with pytest.raises(DeviceNotFoundError):
        device_core.get_device_by_identifier("test-device")


def test_delete_device_not_found(session: Session):
    """Test deleting a device that does not exist."""
    device_core = DeviceCore()
    with pytest.raises(DeviceNotFoundError):
        device_core.delete_device("non-existent-device")
