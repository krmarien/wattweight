"""Measurement management CLI command."""

import argparse
from datetime import datetime
from typing import Optional

from tabulate import tabulate

from wattweight.cli.base import BaseCommand
from wattweight.core.device import DeviceManager, DeviceNotFoundError
from wattweight.core.measurement import MeasurementManager


class MeasurementCommand(BaseCommand):
    """Command for managing measurements."""

    @classmethod
    def register(self, subparsers: argparse._SubParsersAction) -> None:
        """Register the measurement command and its subcommands.

        Args:
            subparsers: The subparsers action from ArgumentParser
        """
        measurement_parser = subparsers.add_parser(
            "measurement", help="Manage measurements"
        )

        measurement_subparsers = measurement_parser.add_subparsers(
            dest="measurement_action", help="Measurement actions"
        )

        # Add subcommand
        add_parser = measurement_subparsers.add_parser(
            "add", help="Add a new measurement"
        )
        add_parser.add_argument(
            "device_identifier",
            help="Device identifier to which the measurement belongs",
        )
        add_parser.add_argument("value", type=float, help="Measurement value")
        add_parser.add_argument(
            "--timestamp",
            type=datetime.fromisoformat,
            help="Measurement timestamp in ISO format (e.g., 2024-03-09T10:30:00). \
                If not provided, uses current UTC time.",
        )

        # List subcommand
        list_parser = measurement_subparsers.add_parser(
            "list", help="List all measurements for a device"
        )
        list_parser.add_argument(
            "device_identifier", help="Device identifier for which to list measurements"
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the device command.

        Args:
            args: Parsed command arguments

        Returns:
            Exit code
        """
        if not hasattr(args, "measurement_action") or args.measurement_action is None:
            self.logger.warning(
                "No measurement action specified. Use 'wattweight measurement --help'"
            )
            return 1

        manager = MeasurementManager(self.db)

        if args.measurement_action == "add":
            return self._add_measurement(
                manager,
                args.device_identifier,
                args.value,
                getattr(args, "timestamp", None),
            )
        elif args.measurement_action == "list":
            return self._list_measurements(manager, args.device_identifier)
        else:
            self.logger.error(f"Unknown measurement action: {args.measurement_action}")
            return 1

    def _add_measurement(
        self,
        manager: MeasurementManager,
        device_identifier: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> int:
        """Add a new measurement.

        Args:
            manager: MeasurementManager instance
            device_identifier: Identifier of the device to which the measurement belongs
            value: Measurement value
            timestamp: Optional measurement timestamp in UTC. If None, uses current UTC
                time.

        Returns:
            Exit code
        """
        self.logger.debug(
            f"Adding measurement: {device_identifier} ({value}) "
            f"at {timestamp or 'current UTC'}"
        )

        try:
            # Resolve device identifier to device_id
            device_manager = DeviceManager(self.db)
            device = device_manager.get_device_by_identifier(device_identifier)

            _ = manager.add_measurement(
                value=value,
                device=device,
                timestamp=timestamp,
            )
            return 0

        except DeviceNotFoundError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to add measurement: {str(e)}")
            return 1

    def _list_measurements(
        self, manager: MeasurementManager, device_identifier: str
    ) -> int:
        """List all measurements for a specific device.

        Args:
            manager: MeasurementManager instance
            device_identifier: Identifier of the device for which to list measurements

        Returns:
            Exit code
        """
        self.logger.debug(f"Listing all measurements for device: {device_identifier}")

        try:
            # Resolve device identifier to device_id
            device_manager = DeviceManager(self.db)
            device = device_manager.get_device_by_identifier(device_identifier)

            measurements = manager.get_measurements(device)

            if not measurements:
                self.logger.warning("No measurements found")
                return 0

            # Prepare table data
            headers = ["ID", "Timestamp", "Value"]
            data = [
                [measurement.id, measurement.timestamp, measurement.value]
                for measurement in measurements
            ]

            # Print table using tabulate
            print()
            print(tabulate(data, headers=headers, tablefmt="grid"))
            print(f"\nTotal: {len(measurements)} measurements(s)\n")
            return 0

        except DeviceNotFoundError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to list measurements: {str(e)}")
            return 1
