"""Device State Service core business logic."""

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

        if len(device.measurements) == 0:
            logger.debug(
                f"Device {device.identifier} has no measurements, skipping state"
                "update."
            )
            return

        # Detect if device is idle based on last measurement time and idle timeout
        device_idle = True
        # TODO

        if device_idle:
            logger.debug(f"Device {device.identifier} is idle, skipping state update.")
            return

        # Update device average power
        # TODO
