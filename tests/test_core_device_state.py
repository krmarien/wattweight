from datetime import datetime, timedelta, timezone

import pytest

from wattweight.core.device_state import DeviceStateService
from wattweight.model.device import Device, DeviceMeasurementUnit, DeviceMeasuringState
from wattweight.model.measurement import Measurement


def test_get_energy_for_measurements_watt_hours():
    """Test the get_energy_for_measurements function."""
    device = Device(
        id=1,
        identifier="test",
        measuring_state=DeviceMeasuringState.MEASURING,
        idle_timeout=60,
        idle_threshold=10.0,
        measurement_unit=DeviceMeasurementUnit.WATT_HOURS,
    )
    measurements = [
        Measurement(
            id=1,
            value=100.0,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
            device_id=1,
        ),
        Measurement(
            id=2,
            value=150.0,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=50),
            device_id=1,
        ),
        Measurement(
            id=3, value=160.0, timestamp=datetime.now(timezone.utc), device_id=1
        ),
    ]
    energy = DeviceStateService.get_energy_for_measurements(device, measurements)
    assert energy == [50.0, 10.0]


def test_get_energy_for_measurements_watts():
    """Test the get_energy_for_measurements function."""
    device = Device(
        id=1,
        identifier="test",
        measuring_state=DeviceMeasuringState.MEASURING,
        idle_timeout=60,
        idle_threshold=10.0,
        measurement_unit=DeviceMeasurementUnit.WATTS,
    )
    measurements = [
        Measurement(
            id=1,
            value=120.0,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
            device_id=1,
        ),
        Measurement(
            id=2,
            value=90.0,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=50),
            device_id=1,
        ),
        Measurement(
            id=3,
            value=54.0,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=45),
            device_id=1,
        ),
    ]
    energy = DeviceStateService.get_energy_for_measurements(device, measurements)
    assert energy == pytest.approx([17.5, 6])
