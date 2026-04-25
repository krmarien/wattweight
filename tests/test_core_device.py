"""Unit tests for the DeviceCore."""

import pytest
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from wattweight.core.device import (
    DeviceCore,
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
)
from wattweight.core.measurement import MeasurementCore
from wattweight.model.measurement import Measurement


def test_add_device():
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


def test_add_device_already_exists():
    """Test adding a device that already exists."""
    device_core = DeviceCore()
    device_core.add_device(identifier="test-device", name="Test Device")
    with pytest.raises(DeviceAlreadyExistsError):
        device_core.add_device(identifier="test-device", name="Another Device")


def test_get_all_devices():
    """Test getting all devices."""
    device_core = DeviceCore()
    device_core.add_device(identifier="dev1", name="Device 1")
    device_core.add_device(identifier="dev2", name="Device 2")

    devices = device_core.get_all_devices()
    assert len(devices) == 2


def test_get_device_by_identifier():
    """Test getting a device by its identifier."""
    device_core = DeviceCore()
    device_core.add_device(identifier="test-device", name="Test Device")

    device = device_core.get_device_by_identifier("test-device")
    assert device is not None
    assert device.name == "Test Device"


def test_get_device_by_identifier_not_found():
    """Test getting a device that does not exist."""
    device_core = DeviceCore()
    with pytest.raises(DeviceNotFoundError):
        device_core.get_device_by_identifier("non-existent-device")


def test_update_device():
    """Test updating a device."""
    device_core = DeviceCore()
    _ = device_core.add_device(identifier="test-device", name="Test Device")

    updated_device = device_core.update_device(
        identifier="test-device",
        name="Updated Name",
        description="Updated Description",
        measurement_unit="WATT_HOURS",
    )

    assert updated_device.name == "Updated Name"
    assert updated_device.description == "Updated Description"


def test_update_device_not_found():
    """Test updating a device that does not exist."""
    device_core = DeviceCore()
    with pytest.raises(DeviceNotFoundError):
        device_core.update_device(identifier="non-existent-device", name="New Name")


def test_update_device_no_fields():
    """Test updating a device with no fields."""
    device_core = DeviceCore()
    device_core.add_device(identifier="test-device", name="Test Device")
    with pytest.raises(ValueError):
        device_core.update_device(identifier="test-device")


def test_update_device_idle_timeout():
    """Test updating only the idle_timeout of a device."""
    device_core = DeviceCore()
    device_core.add_device(
        identifier="test-device", name="Test Device", idle_timeout=100
    )
    updated_device = device_core.update_device(
        identifier="test-device", idle_timeout=200
    )
    assert updated_device.idle_timeout == 200


def test_update_device_idle_energy_threshold():
    """Test updating only the idle_energy_threshold of a device."""
    device_core = DeviceCore()
    device_core.add_device(
        identifier="test-device", name="Test Device", idle_energy_threshold=5.0
    )
    updated_device = device_core.update_device(
        identifier="test-device", idle_energy_threshold=10.0
    )
    assert updated_device.idle_energy_threshold == 10.0


def test_delete_device():
    """Test deleting a device."""
    device_core = DeviceCore()
    _ = device_core.add_device(identifier="test-device", name="Test Device")

    device_core.delete_device("test-device")

    with pytest.raises(DeviceNotFoundError):
        device_core.get_device_by_identifier("test-device")


def test_delete_device_with_measurements():
    """Test deleting a device with measurements."""
    device_core = DeviceCore()
    measurement_core = MeasurementCore()
    device = device_core.add_device(identifier="test-device", name="Test Device")

    measurement_core.add_measurement(
        value=100.0,
        device=device,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    measurement_core.add_measurement(
        value=150.0,
        device=device,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=3),
    )

    device2 = device_core.add_device(identifier="test-device2", name="Test Device2")
    measurement_core.add_measurement(value=110.0, device=device2)

    device_core.delete_device("test-device")

    with pytest.raises(DeviceNotFoundError):
        device_core.get_device_by_identifier("test-device")

    measurements = device_core.db.exec(select(Measurement)).all()

    assert len(measurements) == 1


def test_delete_device_not_found():
    """Test deleting a device that does not exist."""
    device_core = DeviceCore()
    with pytest.raises(DeviceNotFoundError):
        device_core.delete_device("non-existent-device")
