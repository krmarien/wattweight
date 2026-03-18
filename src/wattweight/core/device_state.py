"""Device State Service core business logic."""

from datetime import timezone, datetime

from sqlmodel import select

from wattweight.database import Database
from wattweight.model.measurement import Measurement
from wattweight.logger import Logger
from wattweight.model.device import Device


class DeviceStateService:
    @staticmethod
    def update_state(device: Device):
        """Update the state of a device based on its last measurement time and idle
            timeout.

        Args:
            device: The device to update
        """

        logger = Logger()
        db = Database().get_session()

        if len(device.measurements) == 0:
            logger.debug(
                f"Device {device.identifier} has no measurements, skipping state"
                "update."
            )
            return

        # Detect if device is idle based on last measurement time and idle timeout
        device_idle = DeviceStateService.is_device_idle(device)

        if not device_idle:
            logger.debug(
                f"Device {device.identifier} is not idle, skipping state update."
            )
            return

        # Update device average power
        # TODO

        # Remove all measurements for this device
        for measurement in device.measurements:
            db.delete(measurement)

        db.commit()

    @staticmethod
    def is_device_idle(device: Device):
        db = Database().get_session()
        logger = Logger()

        # Get measurements for this device in the last device.idle_timeout seconds
        # and check the are about the device.idle_threshold
        idle_measurements = db.exec(
            select(Measurement).where(
                Measurement.device_id == device.id,
                Measurement.timestamp
                > int(datetime.now(timezone.utc).timestamp()) - device.idle_timeout,
            )
        ).all()

        if len(idle_measurements) > 0:
            above_threshold = [
                m for m in idle_measurements if m.value > device.idle_power
            ]
            logger.debug(
                f"Device {device.identifier} has {len(above_threshold)} measurements"
                f"above the idle threshold in the last {device.idle_timeout} seconds."
            )
            return len(above_threshold) == 0
        else:
            logger.debug(
                f"No measurements found for device {device.identifier} in the last"
                f"{device.idle_timeout} seconds."
            )
            return True
