"""Measurement management core business logic."""

from datetime import datetime
from typing import List, Optional

from sqlmodel import select

from wattweight.database import Database
from wattweight.model import Measurement
from wattweight.model.device import Device
from wattweight.core.base import BaseManager


class MeasurementManager(BaseManager):
    """Manager for measurement operations."""

    def __init__(self, db: Database):
        """Initialize the measurement manager.

        Args:
            db: Database instance
        """
        super().__init__(db)

    def add_measurement(
        self,
        value: float,
        device_id: int,
        timestamp: Optional[datetime] = None,
    ) -> Measurement:
        """Add a new measurement.

        Args:
            value: Measurement value
            device_id: ID of the device to which the measurement belongs
            timestamp: Optional measurement timestamp in UTC. If None, uses current UTC
                time.

        Returns:
            The created Measurement object

        Raises:
            Exception: If database operation fails
        """
        session = self._get_session()

        # Create and add measurement
        measurement = Measurement(
            value=value,
            device_id=device_id,
            timestamp=timestamp,
        )
        session.add(measurement)
        session.commit()
        session.refresh(measurement)

        return measurement

    def get_measurements(self, device: Device) -> List[Measurement]:
        """Get all measurements for a device by its identifier.

        Args:
            device: The device for which to get measurements

        Returns:
            List of all Measurement objects for the specified device

        Raises:
            DeviceNotFoundError: If device is not found
        """
        session = self._get_session()

        measurements = session.exec(
            select(Measurement).where(Measurement.device_id == device.id)
        ).all()
        return measurements
