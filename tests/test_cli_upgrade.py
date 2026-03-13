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
    with patch("wattweight.cli.base.get_logger", return_value=logger):
        return UpgradeCommand(db)


def test_register():
    """Test the register method."""
    subparsers = MagicMock()
    UpgradeCommand.register(subparsers)
    subparsers.add_parser.assert_called_with("db", help="Database management commands")


def test_execute_no_action(upgrade_command: UpgradeCommand, logger: Logger):
    """Test execute with no action."""
    with patch("wattweight.cli.base.get_logger", return_value=logger):
        args = argparse.Namespace()
        result = upgrade_command.execute(args)
        assert result == 1
        logger.warning.assert_called_with(
            "No database action specified. Use 'wattweight db --help'"
        )


def test_execute_unknown_action(upgrade_command: UpgradeCommand, logger: Logger):
    """Test execute with an unknown action."""
    with patch("wattweight.cli.base.get_logger", return_value=logger):
        args = argparse.Namespace(db_action="unknown")
        result = upgrade_command.execute(args)
        assert result == 1
        logger.error.assert_called_with("Unknown database action: unknown")


@patch("wattweight.cli.upgrade.MigrationManager")
@patch("wattweight.cli.base.get_logger")
def test_upgrade_database_success(
    mock_get_logger, mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test upgrading the database successfully."""
    mock_get_logger.return_value = logger
    args = argparse.Namespace(db_action="upgrade")
    result = upgrade_command.execute(args)
    assert result == 0
    mock_manager.return_value.upgrade.assert_called_once()
    logger.info.assert_called_with("Database upgraded successfully")


@patch("wattweight.cli.upgrade.MigrationManager")
@patch("wattweight.cli.base.get_logger")
def test_upgrade_database_runtime_error(
    mock_get_logger, mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test upgrading the database with a failure."""
    mock_get_logger.return_value = logger
    mock_manager.return_value.upgrade.side_effect = RuntimeError("Upgrade failed")
    args = argparse.Namespace(db_action="upgrade")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Upgrade failed")


@patch("wattweight.cli.upgrade.MigrationManager")
@patch("wattweight.cli.base.get_logger")
def test_upgrade_database_exception(
    mock_get_logger, mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test a generic exception when upgrading the database."""
    mock_get_logger.return_value = logger
    mock_manager.return_value.upgrade.side_effect = Exception("Random error")
    args = argparse.Namespace(db_action="upgrade")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to upgrade database: Random error")


@patch("wattweight.cli.upgrade.MigrationManager")
@patch("wattweight.cli.base.get_logger")
def test_create_migration_success(
    mock_get_logger, mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test creating a migration successfully."""
    mock_get_logger.return_value = logger
    args = argparse.Namespace(db_action="migrate", message="New migration")
    result = upgrade_command.execute(args)
    assert result == 0
    mock_manager.return_value.create_migration.assert_called_with("New migration")
    logger.info.assert_called_with("Migration created successfully")


@patch("wattweight.cli.upgrade.MigrationManager")
@patch("wattweight.cli.base.get_logger")
def test_create_migration_runtime_error(
    mock_get_logger, mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test creating a migration with a failure."""
    mock_get_logger.return_value = logger
    mock_manager.return_value.create_migration.side_effect = RuntimeError(
        "Migration failed"
    )
    args = argparse.Namespace(db_action="migrate", message="New migration")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Migration failed")


@patch("wattweight.cli.upgrade.MigrationManager")
@patch("wattweight.cli.base.get_logger")
def test_create_migration_exception(
    mock_get_logger, mock_manager, upgrade_command: UpgradeCommand, logger: Logger
):
    """Test a generic exception when creating a migration."""
    mock_get_logger.return_value = logger
    mock_manager.return_value.create_migration.side_effect = Exception("Random error")
    args = argparse.Namespace(db_action="migrate", message="New migration")
    result = upgrade_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to create migration: Random error")
