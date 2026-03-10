"""Device management core business logic."""

from typing import List, Optional

from sqlmodel import select

from wattweight.database import Database
from wattweight.model import Device
from wattweight.core.base import BaseManager


class DeviceNotFoundError(Exception):
    """Raised when a device is not found."""

    pass


class DeviceAlreadyExistsError(Exception):
    """Raised when trying to create a device that already exists."""

    pass


class DeviceManager(BaseManager):
    """Manager for device operations."""

    def __init__(self, db: Database):
        """Initialize the device manager.

        Args:
            db: Database instance
        """
        super().__init__(db)

    def add_device(
        self,
        identifier: str,
        name: str,
        description: Optional[str] = None,
        idle_timeout: int = 20 * 60,
        idle_power: float = 2.0,
    ) -> Device:
        """Add a new device.

        Args:
            identifier: Device identifier (must be unique)
            name: Device name
            description: Optional device description
            idle_timeout: Idle timeout in seconds (default: 1200)
            idle_power: Power consumption when idle in watts (default: 2.0)

        Returns:
            The created Device object

        Raises:
            DeviceAlreadyExistsError: If a device with the same identifier exists
            Exception: If database operation fails
        """
        session = self._get_session()

        # Check if device already exists
        existing = session.exec(
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
        session.add(device)
        session.commit()
        session.refresh(device)

        return device

    def get_all_devices(self) -> List[Device]:
        """Get all devices.

        Returns:
            List of all Device objects
        """
        session = self._get_session()
        devices = session.exec(select(Device)).all()
        return devices

    def get_device_by_identifier(self, identifier: str) -> Device:
        """Get a device by identifier.

        Args:
            identifier: Device identifier

        Returns:
            The Device object

        Raises:
            DeviceNotFoundError: If device is not found
        """
        session = self._get_session()
        device = session.exec(
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
        """Update a device.

        Args:
            identifier: Device identifier
            name: New device name (optional)
            description: New device description (optional)
            idle_timeout: New idle timeout in seconds (optional)
            idle_power: New idle power in watts (optional)

        Returns:
            The updated Device object

        Raises:
            DeviceNotFoundError: If device is not found
            ValueError: If no fields are provided to update
        """
        if all(v is None for v in [name, description, idle_timeout, idle_power]):
            raise ValueError("At least one field must be provided to update")

        session = self._get_session()
        device = session.exec(
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

        session.add(device)
        session.commit()
        session.refresh(device)

        return device

    def delete_device(self, identifier: str) -> None:
        """Delete a device.

        Args:
            identifier: Device identifier

        Raises:
            DeviceNotFoundError: If device is not found
        """
        session = self._get_session()
        device = session.exec(
            select(Device).where(Device.identifier == identifier)
        ).first()

        if not device:
            raise DeviceNotFoundError(
                f"Device with identifier '{identifier}' not found"
            )

        session.delete(device)
        session.commit()
