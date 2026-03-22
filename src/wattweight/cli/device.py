"""Device management CLI command."""

import argparse
from typing import Optional

from tabulate import tabulate

from wattweight.cli.base import BaseCommand
from wattweight.core.device import (
    DeviceCore,
    DeviceNotFoundError,
    DeviceAlreadyExistsError,
)


class DeviceCommand(BaseCommand):
    """Command for managing devices."""

    def __init__(self):
        super().__init__()

    @classmethod
    def register(self, subparsers: argparse._SubParsersAction) -> None:
        """Register the device command and its subcommands.

        Args:
            subparsers: The subparsers action from ArgumentParser
        """
        device_parser = subparsers.add_parser("device", help="Manage devices")

        device_subparsers = device_parser.add_subparsers(
            dest="device_action", help="Device actions"
        )

        # Add subcommand
        add_parser = device_subparsers.add_parser("add", help="Add a new device")
        add_parser.add_argument("identifier", help="Device identifier (unique)")
        add_parser.add_argument("name", help="Device name")
        add_parser.add_argument("--description", help="Device description")
        add_parser.add_argument(
            "--idle-timeout",
            type=int,
            default=20 * 60,
            help="Idle timeout in seconds (default: 1200)",
        )
        add_parser.add_argument(
            "--idle-energy-threshold",
            type=float,
            default=2.0,
            help="Idle energy threshold in watthours (default: 2.0)",
        )
        add_parser.add_argument(
            "--measurement-unit",
            choices=["watts", "watt_hours"],
            default="watt_hours",
            help="Measurement unit for the device (default: watt_hours)",
        )

        # List subcommand
        device_subparsers.add_parser("list", help="List all devices")

        # Modify subcommand
        modify_parser = device_subparsers.add_parser("modify", help="Modify a device")
        modify_parser.add_argument("identifier", help="Device identifier to modify")
        modify_parser.add_argument("--name", help="New device name")
        modify_parser.add_argument("--description", help="New device description")
        modify_parser.add_argument(
            "--idle-timeout", type=int, help="New idle timeout in seconds"
        )
        modify_parser.add_argument(
            "--idle-energy-threshold",
            type=float,
            help="New idle energy threshold in watthours",
        )
        modify_parser.add_argument(
            "--measurement-unit",
            choices=["watts", "watt_hours"],
            help="New measurement unit for the device",
        )

        # Remove subcommand
        remove_parser = device_subparsers.add_parser("remove", help="Remove a device")
        remove_parser.add_argument("identifier", help="Device identifier to remove")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the device command.

        Args:
            args: Parsed command arguments

        Returns:
            Exit code
        """
        if not hasattr(args, "device_action") or args.device_action is None:
            self.logger.warning(
                "No device action specified. Use 'wattweight device --help'"
            )
            return 1

        if args.device_action == "add":
            return self._add_device(
                args.identifier,
                args.name,
                args.description,
                args.idle_timeout,
                args.idle_energy_threshold,
                args.measurement_unit,
            )
        elif args.device_action == "list":
            return self._list_devices()
        elif args.device_action == "modify":
            return self._modify_device(
                args.identifier,
                args.name,
                args.description,
                args.idle_timeout,
                args.idle_energy_threshold,
                args.measurement_unit,
            )
        elif args.device_action == "remove":
            return self._remove_device(args.identifier)
        else:
            self.logger.error(f"Unknown device action: {args.device_action}")
            return 1

    def _add_device(
        self,
        identifier: str,
        name: str,
        description: Optional[str] = None,
        idle_timeout: int = 20 * 60,
        idle_energy_threshold: float = 2.0,
        measurement_unit: str = "watts",
    ) -> int:
        """Add a new device.

        Args:
            identifier: Device identifier
            name: Device name
            description: Device description (optional)
            idle_timeout: Idle timeout in seconds
            idle_energy_threshold: Idle energy threshold in watthours
            measurement_unit: Measurement unit for the device
        Returns:
            Exit code
        """
        self.logger.debug(f"Adding device: {identifier} ({name})")

        try:
            device_core = DeviceCore()
            _ = device_core.add_device(
                identifier,
                name,
                description=description,
                idle_timeout=idle_timeout,
                idle_energy_threshold=idle_energy_threshold,
                measurement_unit=measurement_unit,
            )
            return 0

        except DeviceAlreadyExistsError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to add device: {str(e)}")
            return 1

    def _list_devices(self) -> int:
        """List all devices.

        Returns:
            Exit code
        """
        self.logger.debug("Listing all devices")

        try:
            device_core = DeviceCore()
            devices = device_core.get_all_devices()

            if not devices:
                self.logger.warning("No devices found")
                return 0

            # Prepare table data
            headers = [
                "ID",
                "Identifier",
                "Name",
                "Idle Timeout (s)",
                "Idle Energy Threshold (Wh)",
                "State",
                "Unit",
                "Measuring State",
            ]
            data = [
                [
                    device.id,
                    device.identifier,
                    device.name,
                    device.idle_timeout,
                    device.idle_energy_threshold,
                    device.state.value,
                    device.measurement_unit.value,
                    device.measuring_state.value,
                ]
                for device in devices
            ]

            # Print table using tabulate
            print()
            print(tabulate(data, headers=headers, tablefmt="grid"))
            print(f"Total: {len(devices)} device(s)\\n")
            return 0

        except Exception as e:
            self.logger.error(f"Failed to list devices: {str(e)}")
            return 1

    def _modify_device(
        self,
        identifier: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        idle_timeout: Optional[int] = None,
        idle_energy_threshold: Optional[float] = None,
        measurement_unit: Optional[str] = None,
    ) -> int:
        """Modify a device.

        Args:
            identifier: Device identifier to modify
            name: New device name (optional)
            description: New device description (optional)
            idle_timeout: New idle timeout in seconds (optional)
            idle_energy_threshold: New idle energy threshold in watthours (optional)
            measurement_unit: New measurement unit (optional)

        Returns:
            Exit code
        """
        self.logger.debug(f"Modifying device: {identifier}")

        try:
            device_core = DeviceCore()
            device_core.update_device(
                identifier,
                name=name,
                description=description,
                idle_timeout=idle_timeout,
                idle_energy_threshold=idle_energy_threshold,
                measurement_unit=measurement_unit,
            )
            return 0

        except DeviceNotFoundError as e:
            self.logger.error(str(e))
            return 1
        except ValueError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to modify device: {str(e)}")
            return 1

    def _remove_device(self, identifier: str) -> int:
        """Remove a device.

        Args:
            identifier: Device identifier to remove

        Returns:
            Exit code
        """
        self.logger.debug(f"Removing device: {identifier}")

        try:
            device_core = DeviceCore()
            device_core.delete_device(identifier)
            return 0

        except DeviceNotFoundError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to remove device: {str(e)}")
            return 1
