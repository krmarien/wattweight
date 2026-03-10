"""Main module for wattweight."""

import argparse
import sys
from importlib.metadata import version, PackageNotFoundError

from wattweight.cli.measurement import MeasurementCommand
from wattweight.database import Database
from wattweight.logger import get_logger, set_log_level, LogLevel
from wattweight.cli import DeviceCommand, UpgradeCommand
from wattweight.core.base import BaseManager


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

    # Create database instance for command registration
    db = Database()
    logger = get_logger()

    # Register all commands
    device_cmd = DeviceCommand(db, logger)
    device_cmd.register(subparsers)

    upgrade_cmd = UpgradeCommand(db, logger)
    upgrade_cmd.register(subparsers)

    measurement_cmd = MeasurementCommand(db, logger)
    measurement_cmd.register(subparsers)

    args = parser.parse_args()

    # Configure logging based on verbosity
    if args.verbose == 0:
        set_log_level(LogLevel.WARNING)
    elif args.verbose == 1:
        set_log_level(LogLevel.INFO)
    else:  # args.verbose >= 2
        set_log_level(LogLevel.DEBUG)

    if args.command is None:
        parser.print_help()
        return 0

    # Initialize database with context manager
    with Database() as db:
        logger = get_logger()

        # Create a shared session for all managers
        session = db.get_session()
        BaseManager.set_session(session)

        try:
            # Execute commands
            if args.command == "device":
                command = DeviceCommand(db, logger)
                return command.execute(args)
            elif args.command == "db":
                command = UpgradeCommand(db, logger)
                return command.execute(args)
            elif args.command == "measurement":
                command = MeasurementCommand(db, logger)
                return command.execute(args)
            else:
                logger.error(f"Unknown command: {args.command}")
                return 1
        finally:
            # Clean up: reset the shared session
            session.close()
            BaseManager.set_session(None)


if __name__ == "__main__":
    sys.exit(main())
