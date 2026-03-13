"""Unit tests for the UpgradeCommand."""

import argparse
from unittest.mock import MagicMock, patch

import pytest
from typing import Generator

from wattweight.database import Database
from wattweight.cli.upgrade import UpgradeCommand
from wattweight.logger import Logger


@pytest.fixture
def db() -> Generator[Database, None, None]:
    """Fixture for an in-memory database."""
    database = Database(db_dir=None)
    with database as db_conn:
        yield db_conn


@pytest.fixture
def logger() -> Logger:
    """Fixture for the Logger."""
    return MagicMock(spec=Logger)


@pytest.fixture
def upgrade_command(db: Database, logger: Logger) -> UpgradeCommand:
    """Fixture for the UpgradeCommand."""
    return UpgradeCommand(db, logger)


def test_register(upgrade_command: UpgradeCommand):
    """Test the register method."""
    subparsers = MagicMock()
    upgrade_command.register(subparsers)
    subparsers.add_parser.assert_called_with("db", help="Database management commands")


def test_execute_no_action(upgrade_command: UpgradeCommand, logger: Logger):
    """Test execute with no action."""
    args = argparse.Namespace()
    result = upgrade_command.execute(args)
    assert result == 1
    logger.warning.assert_called_with(
        "No database action specified. Use 'wattweight db --help'"
    )


def test_execute_unknown_action(upgrade_command: UpgradeCommand, logger: Logger):
    """Test execute with an unknown action."""
    args = argparse.Namespace(db_action="unknown")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Unknown database action: unknown")


@patch("wattweight.cli.upgrade.MigrationManager")
def test_upgrade_database_success(
    mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test upgrading the database successfully."""
    args = argparse.Namespace(db_action="upgrade")
    result = upgrade_command.execute(args)
    assert result == 0
    mock_manager.return_value.upgrade.assert_called_once()
    logger.info.assert_called_with("Database upgraded successfully")


@patch("wattweight.cli.upgrade.MigrationManager")
def test_upgrade_database_runtime_error(
    mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test upgrading the database with a failure."""
    mock_manager.return_value.upgrade.side_effect = RuntimeError("Upgrade failed")
    args = argparse.Namespace(db_action="upgrade")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Upgrade failed")


@patch("wattweight.cli.upgrade.MigrationManager")
def test_upgrade_database_exception(
    mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test a generic exception when upgrading the database."""
    mock_manager.return_value.upgrade.side_effect = Exception("Random error")
    args = argparse.Namespace(db_action="upgrade")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to upgrade database: Random error")


@patch("wattweight.cli.upgrade.MigrationManager")
def test_create_migration_success(
    mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test creating a migration successfully."""
    args = argparse.Namespace(db_action="migrate", message="New migration")
    result = upgrade_command.execute(args)
    assert result == 0
    mock_manager.return_value.create_migration.assert_called_with("New migration")
    logger.info.assert_called_with("Migration created successfully")


@patch("wattweight.cli.upgrade.MigrationManager")
def test_create_migration_runtime_error(
    mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test creating a migration with a failure."""
    mock_manager.return_value.create_migration.side_effect = RuntimeError(
        "Migration failed"
    )
    args = argparse.Namespace(db_action="migrate", message="New migration")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Migration failed")


@patch("wattweight.cli.upgrade.MigrationManager")
def test_create_migration_exception(
    mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test a generic exception when creating a migration."""
    mock_manager.return_value.create_migration.side_effect = Exception("Random error")
    args = argparse.Namespace(db_action="migrate", message="New migration")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to create migration: Random error")
