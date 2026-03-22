from datetime import datetime
from typing import List, Optional

from sqlmodel import select

from wattweight.core.base import Core
from wattweight.core.device_state import DeviceStateService
from wattweight.model import Measurement
from wattweight.model.device import Device


class MeasurementCore(Core):
    """Core class for measurement operations."""

    def add_measurement(
        self,
        value: float,
        device: Device,
        timestamp: Optional[datetime] = None,
    ) -> Measurement:
        """Add a new measurement."""

        # Create and add measurement
        measurement = Measurement(
            value=value,
            device_id=device.id,
            timestamp=timestamp,
        )
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)

        DeviceStateService.update_state(self.db.get(Device, device.id))

        return measurement

    def get_measurements(self, device: Device) -> List[Measurement]:
        """Get all measurements for a device by its identifier."""
        measurements = self.db.exec(
            select(Measurement).where(Measurement.device_id == device.id)
        ).all()
        return measurements
