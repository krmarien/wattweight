"""Measurement management CLI command."""

import argparse
import json

from tabulate import tabulate

from wattweight.cli.base import BaseCommand
from wattweight.core.average_usage import AverageUsageCore
from wattweight.core.device import DeviceCore, DeviceNotFoundError


class AverageUsageCommand(BaseCommand):
    """Command for managing average usage."""

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def register(
        cls, subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]"
    ) -> None:
        """Register the average usage command and its subcommands.

        Args:
            subparsers: The subparsers action from ArgumentParser
        """
        average_usage_parser = subparsers.add_parser(
            "average-usage", help="Manage average usage"
        )

        average_usage_subparsers = average_usage_parser.add_subparsers(
            dest="average_usage_action", help="Average usage actions"
        )

        # List subcommand
        list_parser = average_usage_subparsers.add_parser(
            "list", help="List all average usage entries for a device"
        )
        list_parser.add_argument(
            "device_identifier",
            help="Device identifier for which to list average usage entries",
        )
        list_parser.add_argument(
            "--json",
            action="store_true",
            help="Output average usage entries in JSON format",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the device command.

        Args:
            args: Parsed command arguments

        Returns:
            Exit code
        """
        if (
            not hasattr(args, "average_usage_action")
            or args.average_usage_action is None
        ):
            self.logger.warning(
                "No average usage action specified. Use 'wattweight average-usage"
                " --help'"
            )
            return 1

        if args.average_usage_action == "list":
            return self._list_average_usages(args.device_identifier, args.json)
        else:
            self.logger.error(
                f"Unknown average usage action: {args.average_usage_action}"
            )
            return 1

    def _list_average_usages(
        self, device_identifier: str, json_output: bool = False
    ) -> int:
        """List all average usage entries for a specific device.

        Args:
            device_identifier: Identifier of the device for which to list average
                usage entries
            json_output: Whether to output average usage entries in JSON format

        Returns:
            Exit code
        """
        self.logger.debug(
            f"Listing all average usage entries for device: {device_identifier}"
        )

        try:
            device_core = DeviceCore()
            average_usage_core = AverageUsageCore()
            # Resolve device identifier to device_id
            device = device_core.get_device_by_identifier(device_identifier)

            average_usages = average_usage_core.get_average_usage(device)

            if not average_usages:
                self.logger.warning("No average usage entries found")
                return 0

            if json_output:
                json_data = [
                    {
                        "id": average_usage.id,
                        "timestamp": average_usage.timestamp.isoformat(),
                        "value": average_usage.value,
                    }
                    for average_usage in average_usages
                ]
                print(json.dumps(json_data, indent=2))
            else:
                # Prepare table data
                headers = ["ID", "Minutes", "Value"]
                table_data = [
                    [
                        average_usage.id,
                        average_usage.timestamp.timestamp() / 60,
                        average_usage.value,
                    ]
                    for average_usage in average_usages
                ]

                # Print table using tabulate
                print()
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print(f"Total: {len(average_usages)} average usage entry(s)\\n")
            return 0

        except DeviceNotFoundError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to list average usage entries: {str(e)}")
            return 1
