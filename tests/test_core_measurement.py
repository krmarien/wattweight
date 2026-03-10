"""Unit tests for the MeasurementManager."""

import pytest
from typing import Generator

from wattweight.database import Database
from wattweight.core.device import DeviceManager
from wattweight.core.measurement import MeasurementManager
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


@pytest.fixture
def measurement_manager(db: Database) -> MeasurementManager:
    """Fixture for the MeasurementManager."""
    return MeasurementManager(db)


@pytest.fixture
def device(device_manager: DeviceManager) -> Device:
    """Fixture for a test device."""
    return device_manager.add_device(identifier="test-device", name="Test Device")


def test_add_measurement(measurement_manager: MeasurementManager, device: Device):
    """Test adding a new measurement."""
    measurement = measurement_manager.add_measurement(
        value=100.0,
        device_id=device.id,
    )
    assert measurement.value == 100.0
    assert measurement.device_id == device.id


def test_get_measurements(measurement_manager: MeasurementManager, device: Device):
    """Test getting all measurements for a device."""
    measurement_manager.add_measurement(value=100.0, device_id=device.id)
    measurement_manager.add_measurement(value=110.0, device_id=device.id)

    measurements = measurement_manager.get_measurements(device)
    assert len(measurements) == 2


def test_get_measurements_for_device_with_no_measurements(
    measurement_manager: MeasurementManager, device: Device
):
    """Test getting measurements for a device with no measurements."""
    measurements = measurement_manager.get_measurements(device)
    assert len(measurements) == 0
