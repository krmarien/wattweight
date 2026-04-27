"""Unit tests for the MeasurementCore."""

from datetime import datetime, timedelta, timezone

import pytest

from wattweight.core.average_usage import AverageUsageCore
from wattweight.core.device import DeviceCore
from wattweight.core.device_state import DeviceStateService
from wattweight.core.measurement import MeasurementCore
from wattweight.model.device import Device


@pytest.fixture
def device() -> Device:
    """Fixture for a test device."""
    device_core = DeviceCore()
    return device_core.add_device(
        identifier="test-device", name="Test Device", measurement_unit="WATT_HOURS"
    )


def test_list_average_usage(device: Device):
    """Test listing average usage for a device."""
    measurement_core = MeasurementCore()
    average_usage_core = AverageUsageCore()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "wattweight.core.device_state.DeviceStateService.update_state",
            lambda *args: "mocked",
        )
        _ = measurement_core.add_measurement(
            value=100.0,
            device=device,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=35),
        )
    _ = measurement_core.add_measurement(
        value=130.0,
        device=device,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=25),
    )

    average_usage = average_usage_core.get_average_usage(device)
    assert len(average_usage) == 10 / DeviceStateService.SAMPLE_FREQUENCY_MINUTES
    for i in range(len(average_usage) - 1):
        assert (
            average_usage[i + 1].timestamp / 60 - average_usage[i].timestamp / 60
            == DeviceStateService.SAMPLE_FREQUENCY_MINUTES
        )
    assert sum([x.value for x in average_usage]) == pytest.approx(30)
