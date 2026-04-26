"""Main module for wattweight."""

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version

from wattweight.cli.average_usage import AverageUsageCommand
from wattweight.cli.device import DeviceCommand
from wattweight.cli.measurement import MeasurementCommand
from wattweight.cli.upgrade import UpgradeCommand
from wattweight.database import Database
from wattweight.logger import Logger, LogLevel


def get_version() -> str:
    """Get the version from package metadata."""
    try:
        return version("wattweight")
    except PackageNotFoundError:
        return "dev"


def main() -> int:
    """Main entry point for the wattweight application."""
    parser = argparse.ArgumentParser(
        description="Wattweight - Energy management tool", prog="wattweight"
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (-v for INFO, -vv for DEBUG)",
    )

    # Create subparsers before registering commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register all commands
    DeviceCommand.register(subparsers)
    UpgradeCommand.register(subparsers)
    MeasurementCommand.register(subparsers)
    AverageUsageCommand.register(subparsers)
    args = parser.parse_args()

    logger = Logger()

    # Configure logging based on verbosity
    if args.verbose == 0:
        logger.set_level(LogLevel.WARNING)
    elif args.verbose == 1:
        logger.set_level(LogLevel.INFO)
    else:  # args.verbose >= 2
        logger.set_level(LogLevel.DEBUG)

    if args.command is None:
        parser.print_help()
        return 0

    with Database() as db:
        db.init_db()

        try:
            # Execute commands
            if args.command == "device":
                return DeviceCommand().execute(args)
            elif args.command == "db":
                return UpgradeCommand().execute(args)
            elif args.command == "measurement":
                return MeasurementCommand().execute(args)
            elif args.command == "average-usage":
                return AverageUsageCommand().execute(args)
            else:
                logger.error(f"Unknown command: {args.command}")
                return 1
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
