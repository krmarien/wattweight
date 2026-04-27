"""Unit tests for the AverageUsageCommand."""

import argparse
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from wattweight.cli.average_usage import AverageUsageCommand
from wattweight.core.device import DeviceNotFoundError
from wattweight.logger import Logger


@pytest.fixture
def logger() -> Logger:
    """Fixture for the Logger."""
    return MagicMock(spec=Logger)


@pytest.fixture
def average_usage_command(logger: Logger) -> Generator[AverageUsageCommand, None, None]:
    """Fixture for the AverageUsageCommand."""
    with patch("wattweight.cli.base.Logger", return_value=logger):
        yield AverageUsageCommand()


def test_register():
    """Test the register method."""
    subparsers = MagicMock()
    measurement_parser = MagicMock()
    subparsers.add_parser.return_value = measurement_parser
    AverageUsageCommand.register(subparsers)
    subparsers.add_parser.assert_called_with(
        "average-usage", help="Manage average usage"
    )


def test_execute_no_action(average_usage_command: AverageUsageCommand, logger: Logger):
    """Test execute with no action."""
    args = argparse.Namespace(average_usage_action=None)
    result = average_usage_command.execute(args)
    assert result == 1
    logger.warning.assert_called_with(
        "No average usage action specified. Use 'wattweight average-usage --help'"
    )


def test_execute_unknown_action(
    average_usage_command: AverageUsageCommand, logger: Logger
):
    """Test execute with an unknown action."""
    args = argparse.Namespace(average_usage_action="unknown")
    result = average_usage_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Unknown average usage action: unknown")


@patch("wattweight.cli.average_usage.DeviceCore")
@patch("wattweight.cli.average_usage.AverageUsageCore")
def test_list_average_usages_empty(
    mock_average_usage_core,
    mock_device_core,
    average_usage_command: AverageUsageCommand,
    logger: Logger,
):
    """Test listing average usage entries when none exist."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_average_usage_core.return_value.get_average_usage.return_value = []
    args = argparse.Namespace(
        average_usage_action="list", device_identifier="test", json=False
    )
    result = average_usage_command.execute(args)
    assert result == 0
    logger.warning.assert_called_with("No average usage entries found")


@patch("wattweight.cli.average_usage.DeviceCore")
@patch("wattweight.cli.average_usage.AverageUsageCore")
def test_list_average_usages_table(
    mock_average_usage_core,
    mock_device_core,
    average_usage_command: AverageUsageCommand,
):
    """Test listing average usage entries."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_average_usage = MagicMock()
    mock_average_usage.id = 1
    mock_average_usage.timestamp = 0
    mock_average_usage.value = 100.0
    mock_average_usage_core.return_value.get_average_usage.return_value = [
        mock_average_usage
    ]
    args = argparse.Namespace(
        average_usage_action="list", device_identifier="test", json=False
    )
    with patch("builtins.print"):
        result = average_usage_command.execute(args)
    assert result == 0


@patch("wattweight.cli.average_usage.DeviceCore")
@patch("wattweight.cli.average_usage.AverageUsageCore")
def test_list_average_usages_json(
    mock_average_usage_core,
    mock_device_core,
    average_usage_command: AverageUsageCommand,
):
    """Test listing average usage entries."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_average_usage = MagicMock()
    mock_average_usage.id = 1
    mock_average_usage.timestamp = 0
    mock_average_usage.value = 100.0
    mock_average_usage_core.return_value.get_average_usage.return_value = [
        mock_average_usage
    ]
    args = argparse.Namespace(
        average_usage_action="list", device_identifier="test", json=True
    )
    with patch("builtins.print"):
        result = average_usage_command.execute(args)
    assert result == 0


@patch("wattweight.cli.average_usage.DeviceCore")
def test_list_average_usage_device_not_found(
    mock_device_core, average_usage_command: AverageUsageCommand, logger: Logger
):
    """Test listing average usage for a device that does not exist."""
    mock_device_core.return_value.get_device_by_identifier.side_effect = (
        DeviceNotFoundError("Device not found")
    )
    args = argparse.Namespace(
        average_usage_action="list", device_identifier="test", json=False
    )
    result = average_usage_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device not found")


@patch("wattweight.cli.average_usage.DeviceCore")
@patch("wattweight.cli.average_usage.AverageUsageCore")
def test_list_measurements_exception(
    mock_average_usage_core,
    mock_device_core,
    average_usage_command: AverageUsageCommand,
    logger: Logger,
):
    """Test a generic exception when listing average usage entries."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_average_usage_core.return_value.get_average_usage.side_effect = Exception(
        "Random error"
    )
    args = argparse.Namespace(
        average_usage_action="list", device_identifier="test", json=False
    )
    result = average_usage_command.execute(args)
    assert result == 1
    logger.error.assert_called_with(
        "Failed to list average usage entries: Random error"
    )
