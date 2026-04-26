"""Database upgrade and migration CLI command."""

import argparse

from wattweight.cli.base import BaseCommand
from wattweight.core.migration import MigrationCore


class UpgradeCommand(BaseCommand):
    """Command for managing database upgrades and migrations."""

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def register(cls, subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
        """Register the upgrade command and its subcommands.

        Args:
            subparsers: The subparsers action from ArgumentParser
        """
        upgrade_parser = subparsers.add_parser(
            "db", help="Database management commands"
        )

        db_subparsers = upgrade_parser.add_subparsers(
            dest="db_action", help="Database actions"
        )

        # Upgrade subcommand
        db_subparsers.add_parser(
            "upgrade", help="Upgrade the database to the latest version"
        )

        # Create migration subcommand
        migrate_parser = db_subparsers.add_parser(
            "migrate", help="Create a new database migration"
        )
        migrate_parser.add_argument("message", help="Migration description")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the database command.

        Args:
            args: Parsed command arguments

        Returns:
            Exit code
        """
        if not hasattr(args, "db_action") or args.db_action is None:
            self.logger.warning(
                "No database action specified. Use 'wattweight db --help'"
            )
            return 1

        if args.db_action == "upgrade":
            return self._upgrade_database()
        elif args.db_action == "migrate":
            return self._create_migration(args.message)
        else:
            self.logger.error(f"Unknown database action: {args.db_action}")
            return 1

    def _upgrade_database(self) -> int:
        """Upgrade the database to the latest version.

        Returns:
            Exit code
        """
        self.logger.info("Starting database upgrade...")

        try:
            migration_core = MigrationCore()
            migration_core.upgrade()
            self.logger.info("Database upgraded successfully")
            return 0

        except RuntimeError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to upgrade database: {str(e)}")
            return 1

    def _create_migration(self, message: str) -> int:
        """Create a new database migration.

        Args:
            message: Migration description

        Returns:
            Exit code
        """
        self.logger.info(f"Creating migration: {message}")

        try:
            migration_core = MigrationCore()
            migration_core.create_migration(message)
            self.logger.info("Migration created successfully")
            return 0

        except RuntimeError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Failed to create migration: {str(e)}")
            return 1
