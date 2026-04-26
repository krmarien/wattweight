"""Unit tests for the MeasurementCore."""

from datetime import datetime, timedelta, timezone

import pytest

from wattweight.core.device import DeviceCore
from wattweight.core.measurement import MeasurementCore
from wattweight.model.device import Device, DeviceMeasuringState


@pytest.fixture
def device() -> Device:
    """Fixture for a test device."""
    device_core = DeviceCore()
    return device_core.add_device(identifier="test-device", name="Test Device")


def test_add_measurement(device: Device):
    """Test adding a new measurement."""
    device_core = DeviceCore()
    measurement_core = MeasurementCore()
    measurement = measurement_core.add_measurement(
        value=100.0,
        device=device,
    )
    assert measurement.value == 100.0
    assert measurement.device_id == device.id
    assert device.measuring_state == DeviceMeasuringState.MEASURING

    refreshed_device = device_core.get_device_by_identifier(device.identifier)
    assert refreshed_device.measuring_state == device.measuring_state


def test_get_measurements(device: Device):
    """Test getting all measurements for a device."""
    measurement_core = MeasurementCore()
    measurement_core.add_measurement(
        value=100.0,
        device=device,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    measurement_core.add_measurement(
        value=110.0,
        device=device,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    measurements = measurement_core.get_measurements(device)
    assert len(measurements) == 2


def test_get_measurements_for_device_with_no_measurements(device: Device):
    """Test getting measurements for a device with no measurements."""
    measurement_core = MeasurementCore()
    measurements = measurement_core.get_measurements(device)
    assert len(measurements) == 0
