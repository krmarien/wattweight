"""Unit tests for the MeasurementCommand."""

import argparse
from datetime import datetime, timezone
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from wattweight.cli.measurement import MeasurementCommand
from wattweight.core.device import DeviceNotFoundError
from wattweight.logger import Logger


@pytest.fixture
def logger() -> Logger:
    """Fixture for the Logger."""
    return MagicMock(spec=Logger)


@pytest.fixture
def measurement_command(logger: Logger) -> Generator[MeasurementCommand, None, None]:
    """Fixture for the MeasurementCommand."""
    with patch("wattweight.cli.base.Logger", return_value=logger):
        yield MeasurementCommand()


def test_register():
    """Test the register method."""
    subparsers = MagicMock()
    measurement_parser = MagicMock()
    subparsers.add_parser.return_value = measurement_parser
    MeasurementCommand.register(subparsers)
    subparsers.add_parser.assert_called_with("measurement", help="Manage measurements")


def test_execute_no_action(measurement_command: MeasurementCommand, logger: Logger):
    """Test execute with no action."""
    args = argparse.Namespace(measurement_action=None)
    result = measurement_command.execute(args)
    assert result == 1
    logger.warning.assert_called_with(
        "No measurement action specified. Use 'wattweight measurement --help'"
    )


def test_execute_unknown_action(
    measurement_command: MeasurementCommand, logger: Logger
):
    """Test execute with an unknown action."""
    args = argparse.Namespace(measurement_action="unknown")
    result = measurement_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Unknown measurement action: unknown")


@patch("wattweight.cli.measurement.DeviceCore")
@patch("wattweight.cli.measurement.MeasurementCore")
def test_add_measurement_success(
    mock_measurement_core,
    mock_device_core,
    measurement_command: MeasurementCommand,
    logger: Logger,
):
    """Test adding a measurement successfully."""
    device = MagicMock(id=1)
    mock_device_core.return_value.get_device_by_identifier.return_value = device
    args = argparse.Namespace(
        measurement_action="add",
        device_identifier="test",
        value=100.0,
        timestamp=None,
    )
    result = measurement_command.execute(args)
    assert result == 0
    mock_measurement_core.return_value.add_measurement.assert_called_with(
        value=100.0, device=device, timestamp=None
    )


@patch("wattweight.cli.measurement.DeviceCore")
def test_add_measurement_device_not_found(
    mock_device_core, measurement_command: MeasurementCommand, logger: Logger
):
    """Test adding a measurement for a device that does not exist."""
    mock_device_core.return_value.get_device_by_identifier.side_effect = (
        DeviceNotFoundError("Device not found")
    )
    args = argparse.Namespace(
        measurement_action="add",
        device_identifier="test",
        value=100.0,
        timestamp=None,
    )
    result = measurement_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device not found")


@patch("wattweight.cli.measurement.DeviceCore")
@patch("wattweight.cli.measurement.MeasurementCore")
def test_add_measurement_exception(
    mock_measurement_core,
    mock_device_core,
    measurement_command: MeasurementCommand,
    logger: Logger,
):
    """Test a generic exception when adding a measurement."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_measurement_core.return_value.add_measurement.side_effect = Exception(
        "Random error"
    )
    args = argparse.Namespace(
        measurement_action="add",
        device_identifier="test",
        value=100.0,
        timestamp=None,
    )
    result = measurement_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to add measurement: Random error")


@patch("wattweight.cli.measurement.DeviceCore")
@patch("wattweight.cli.measurement.MeasurementCore")
def test_list_measurements_empty(
    mock_measurement_core,
    mock_device_core,
    measurement_command: MeasurementCommand,
    logger: Logger,
):
    """Test listing measurements when none exist."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_measurement_core.return_value.get_measurements.return_value = []
    args = argparse.Namespace(
        measurement_action="list", device_identifier="test", json=False
    )
    result = measurement_command.execute(args)
    assert result == 0
    logger.warning.assert_called_with("No measurements found")


@patch("wattweight.cli.measurement.DeviceCore")
@patch("wattweight.cli.measurement.MeasurementCore")
def test_list_measurements(
    mock_measurement_core,
    mock_device_core,
    measurement_command: MeasurementCommand,
):
    """Test listing measurements."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_measurement = MagicMock()
    mock_measurement.id = 1
    mock_measurement.timestamp = datetime.now(timezone.utc)
    mock_measurement.value = 100.0
    mock_measurement_core.return_value.get_measurements.return_value = [
        mock_measurement
    ]
    args = argparse.Namespace(
        measurement_action="list", device_identifier="test", json=False
    )
    with patch("builtins.print"):
        result = measurement_command.execute(args)
    assert result == 0


@patch("wattweight.cli.measurement.DeviceCore")
def test_list_measurements_device_not_found(
    mock_device_core, measurement_command: MeasurementCommand, logger: Logger
):
    """Test listing measurements for a device that does not exist."""
    mock_device_core.return_value.get_device_by_identifier.side_effect = (
        DeviceNotFoundError("Device not found")
    )
    args = argparse.Namespace(
        measurement_action="list", device_identifier="test", json=False
    )
    result = measurement_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device not found")


@patch("wattweight.cli.measurement.DeviceCore")
@patch("wattweight.cli.measurement.MeasurementCore")
def test_list_measurements_exception(
    mock_measurement_core,
    mock_device_core,
    measurement_command: MeasurementCommand,
    logger: Logger,
):
    """Test a generic exception when listing measurements."""
    mock_device_core.return_value.get_device_by_identifier.return_value = MagicMock(
        id=1
    )
    mock_measurement_core.return_value.get_measurements.side_effect = Exception(
        "Random error"
    )
    args = argparse.Namespace(
        measurement_action="list", device_identifier="test", json=False
    )
    result = measurement_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to list measurements: Random error")
