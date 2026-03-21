"""Unit tests for the DeviceCommand."""

import argparse
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from wattweight.cli.device import DeviceCommand
from wattweight.core.device import DeviceAlreadyExistsError, DeviceNotFoundError
from wattweight.logger import Logger


@pytest.fixture
def logger() -> Logger:
    """Fixture for the Logger."""
    return MagicMock(spec=Logger)


@pytest.fixture
def device_command(logger: Logger) -> Generator[DeviceCommand, None, None]:
    """Fixture for the DeviceCommand."""
    with patch("wattweight.cli.base.Logger", return_value=logger):
        yield DeviceCommand()


def test_register():
    """Test the register method."""
    subparsers = MagicMock()
    device_parser = MagicMock()
    subparsers.add_parser.return_value = device_parser
    DeviceCommand.register(subparsers)
    subparsers.add_parser.assert_called_with("device", help="Manage devices")


def test_execute_no_action(device_command: DeviceCommand, logger: Logger):
    """Test execute with no action."""
    args = argparse.Namespace(device_action=None)
    result = device_command.execute(args)
    assert result == 1
    logger.warning.assert_called_with(
        "No device action specified. Use 'wattweight device --help'"
    )


def test_execute_unknown_action(device_command: DeviceCommand, logger: Logger):
    """Test execute with an unknown action."""
    args = argparse.Namespace(device_action="unknown")
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Unknown device action: unknown")


@patch("wattweight.cli.device.DeviceCore")
def test_add_device_success(mock_device_core, device_command: DeviceCommand):
    """Test adding a device successfully."""
    mock_device_core.return_value.add_device.return_value = MagicMock(id=1)
    args = argparse.Namespace(
        device_action="add",
        identifier="test",
        name="Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
        measurement_unit="watts",
    )
    result = device_command.execute(args)
    assert result == 0
    mock_device_core.return_value.add_device.assert_called_with(
        "test",
        "Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
        measurement_unit="watts",
    )


@patch("wattweight.cli.device.DeviceCore")
def test_add_device_already_exists(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test adding a device that already exists."""
    mock_device_core.return_value.add_device.side_effect = DeviceAlreadyExistsError(
        "Device already exists"
    )
    args = argparse.Namespace(
        device_action="add",
        identifier="test",
        name="Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
        measurement_unit="watts",
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device already exists")


@patch("wattweight.cli.device.DeviceCore")
def test_add_device_exception(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when adding a device."""
    mock_device_core.return_value.add_device.side_effect = Exception("Random error")
    args = argparse.Namespace(
        device_action="add",
        identifier="test",
        name="Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
        measurement_unit="watts",
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to add device: Random error")


@patch("wattweight.cli.device.DeviceCore")
def test_list_devices_empty(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test listing devices when none exist."""
    mock_device_core.return_value.get_all_devices.return_value = []
    args = argparse.Namespace(device_action="list")
    result = device_command.execute(args)
    assert result == 0
    logger.warning.assert_called_with("No devices found")


@patch("wattweight.cli.device.DeviceCore")
def test_list_devices(mock_device_core, device_command: DeviceCommand, logger: Logger):
    """Test listing devices."""
    mock_device = MagicMock()
    mock_device.id = 1
    mock_device.identifier = "test"
    mock_device.name = "Test Device"
    mock_device.idle_timeout = 1200
    mock_device.idle_power = 2.0
    mock_device.state.value = "Off"
    mock_device.measurement_unit.value = "watts"
    mock_device.measuring_state.value = "NotMeasuring"

    mock_device_core.return_value.get_all_devices.return_value = [mock_device]
    args = argparse.Namespace(device_action="list")
    with patch("builtins.print"):
        result = device_command.execute(args)
    assert result == 0


@patch("wattweight.cli.device.DeviceCore")
def test_list_devices_exception(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when listing devices."""
    mock_device_core.return_value.get_all_devices.side_effect = Exception(
        "Random error"
    )
    args = argparse.Namespace(device_action="list")
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to list devices: Random error")


@patch("wattweight.cli.device.DeviceCore")
def test_modify_device_success(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test modifying a device successfully."""
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description="New Description",
        idle_timeout=600,
        idle_power=1.0,
        measurement_unit="watts",
    )
    result = device_command.execute(args)
    assert result == 0
    mock_device_core.return_value.update_device.assert_called_with(
        "test",
        name="New Name",
        description="New Description",
        idle_timeout=600,
        idle_power=1.0,
        measurement_unit="watts",
    )


@patch("wattweight.cli.device.DeviceCore")
def test_modify_device_not_found(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test modifying a device that does not exist."""
    mock_device_core.return_value.update_device.side_effect = DeviceNotFoundError(
        "Device not found"
    )
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description=None,
        idle_timeout=None,
        idle_power=None,
        measurement_unit=None,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device not found")


@patch("wattweight.cli.device.DeviceCore")
def test_modify_device_value_error(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test a value error when modifying a device."""
    mock_device_core.return_value.update_device.side_effect = ValueError(
        "Invalid value"
    )
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description=None,
        idle_timeout=None,
        idle_power=None,
        measurement_unit=None,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Invalid value")


@patch("wattweight.cli.device.DeviceCore")
def test_modify_device_exception(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when modifying a device."""
    mock_device_core.return_value.update_device.side_effect = Exception("Random error")
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description=None,
        idle_timeout=None,
        idle_power=None,
        measurement_unit=None,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to modify device: Random error")


@patch("wattweight.cli.device.DeviceCore")
def test_remove_device_success(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test removing a device successfully."""
    args = argparse.Namespace(device_action="remove", identifier="test")
    result = device_command.execute(args)
    assert result == 0
    mock_device_core.return_value.delete_device.assert_called_with("test")


@patch("wattweight.cli.device.DeviceCore")
def test_remove_device_not_found(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test removing a device that does not exist."""
    mock_device_core.return_value.delete_device.side_effect = DeviceNotFoundError(
        "Device not found"
    )
    args = argparse.Namespace(device_action="remove", identifier="test")
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device not found")


@patch("wattweight.cli.device.DeviceCore")
def test_remove_device_exception(
    mock_device_core, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when removing a device."""
    mock_device_core.return_value.delete_device.side_effect = Exception("Random error")
    args = argparse.Namespace(device_action="remove", identifier="test")
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to remove device: Random error")
