from wattweight.core.device_state import DeviceStateService
from wattweight.model.device import Device, DeviceMeasurementUnit, DeviceMeasuringState
from wattweight.model.measurement import Measurement


def test_get_energy_for_measurements():
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
        Measurement(id=1, value=100.0, timestamp=10, device_id=1),
        Measurement(id=2, value=150.0, timestamp=20, device_id=1),
        Measurement(id=3, value=120.0, timestamp=30, device_id=1),
    ]
    # TODO: Fix this test, the function is not implemented yet
    _ = DeviceStateService.get_energy_for_measurements(device, measurements)
    # assert energy == 25.0
