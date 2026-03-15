from typing import List, Optional

from sqlmodel import select

from wattweight.core.base import Core
from wattweight.model import Device


class DeviceNotFoundError(Exception):
    """Raised when a device is not found."""

    pass


class DeviceAlreadyExistsError(Exception):
    """Raised when trying to create a device that already exists."""

    pass


class DeviceCore(Core):
    """Core class for device operations."""

    def add_device(
        self,
        identifier: str,
        name: str,
        description: Optional[str] = None,
        idle_timeout: int = 20 * 60,
        idle_power: float = 2.0,
    ) -> Device:
        """Add a new device."""
        # Check if device already exists
        existing = self.db.exec(
            select(Device).where(Device.identifier == identifier)
        ).first()

        if existing:
            raise DeviceAlreadyExistsError(
                f"Device with identifier '{identifier}' already exists"
            )

        # Create and add device
        device = Device(
            identifier=identifier,
            name=name,
            description=description,
            idle_timeout=idle_timeout,
            idle_power=idle_power,
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)

        return device

    def get_all_devices(self) -> List[Device]:
        """Get all devices."""
        devices = self.db.exec(select(Device)).all()
        return devices

    def get_device_by_identifier(self, identifier: str) -> Device:
        """Get a device by identifier."""
        device = self.db.exec(
            select(Device).where(Device.identifier == identifier)
        ).first()

        if not device:
            raise DeviceNotFoundError(
                f"Device with identifier '{identifier}' not found"
            )

        return device

    def update_device(
        self,
        identifier: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        idle_timeout: Optional[int] = None,
        idle_power: Optional[float] = None,
    ) -> Device:
        """Update a device."""
        if all(v is None for v in [name, description, idle_timeout, idle_power]):
            raise ValueError("At least one field must be provided to update")

        device = self.db.exec(
            select(Device).where(Device.identifier == identifier)
        ).first()

        if not device:
            raise DeviceNotFoundError(
                f"Device with identifier '{identifier}' not found"
            )

        # Update fields
        if name is not None:
            device.name = name
        if description is not None:
            device.description = description
        if idle_timeout is not None:
            device.idle_timeout = idle_timeout
        if idle_power is not None:
            device.idle_power = idle_power

        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)

        return device

    def delete_device(self, identifier: str) -> None:
        """Delete a device."""
        device = self.db.exec(
            select(Device).where(Device.identifier == identifier)
        ).first()

        if not device:
            raise DeviceNotFoundError(
                f"Device with identifier '{identifier}' not found"
            )

        for measurement in device.measurements:
            self.db.delete(measurement)

        self.db.delete(device)
        self.db.commit()
