"""Unit tests for the DeviceCommand."""

import argparse
from unittest.mock import MagicMock, patch

import pytest
from typing import Generator

from wattweight.database import Database
from wattweight.cli.device import DeviceCommand
from wattweight.core.device import DeviceAlreadyExistsError, DeviceNotFoundError
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
def device_command(db: Database, logger: Logger) -> DeviceCommand:
    """Fixture for the DeviceCommand."""
    return DeviceCommand(db, logger)


def test_register(device_command: DeviceCommand):
    """Test the register method."""
    subparsers = MagicMock()
    device_command.register(subparsers)
    subparsers.add_parser.assert_called_with("device", help="Manage devices")


def test_execute_no_action(device_command: DeviceCommand, logger: Logger):
    """Test execute with no action."""
    args = argparse.Namespace()
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


@patch("wattweight.cli.device.DeviceManager")
def test_add_device_success(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test adding a device successfully."""
    mock_instance = mock_manager.return_value
    mock_instance.add_device.return_value = MagicMock(id=1)
    args = argparse.Namespace(
        device_action="add",
        identifier="test",
        name="Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
    )
    result = device_command.execute(args)
    assert result == 0
    mock_instance.add_device.assert_called_with(
        "test",
        "Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
    )
    logger.info.assert_called_with("Device 'Test Device' (ID: 1) created successfully")


@patch("wattweight.cli.device.DeviceManager")
def test_add_device_already_exists(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test adding a device that already exists."""
    mock_instance = mock_manager.return_value
    mock_instance.add_device.side_effect = DeviceAlreadyExistsError(
        "Device already exists"
    )
    args = argparse.Namespace(
        device_action="add",
        identifier="test",
        name="Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device already exists")


@patch("wattweight.cli.device.DeviceManager")
def test_add_device_exception(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when adding a device."""
    mock_instance = mock_manager.return_value
    mock_instance.add_device.side_effect = Exception("Random error")
    args = argparse.Namespace(
        device_action="add",
        identifier="test",
        name="Test Device",
        description="A test device",
        idle_timeout=1200,
        idle_power=2.0,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to add device: Random error")


@patch("wattweight.cli.device.DeviceManager")
def test_list_devices_empty(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test listing devices when none exist."""
    mock_instance = mock_manager.return_value
    mock_instance.get_all_devices.return_value = []
    args = argparse.Namespace(device_action="list")
    result = device_command.execute(args)
    assert result == 0
    logger.warning.assert_called_with("No devices found")


@patch("wattweight.cli.device.DeviceManager")
def test_list_devices(mock_manager, device_command: DeviceCommand):
    """Test listing devices."""
    mock_device = MagicMock()
    mock_device.id = 1
    mock_device.identifier = "test"
    mock_device.name = "Test Device"
    mock_device.idle_timeout = 1200
    mock_device.idle_power = 2.0
    mock_device.state.value = "Off"
    mock_device.measuring_state.value = "NotMeasuring"

    mock_instance = mock_manager.return_value
    mock_instance.get_all_devices.return_value = [mock_device]
    args = argparse.Namespace(device_action="list")
    result = device_command.execute(args)
    assert result == 0


@patch("wattweight.cli.device.DeviceManager")
def test_list_devices_exception(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when listing devices."""
    mock_instance = mock_manager.return_value
    mock_instance.get_all_devices.side_effect = Exception("Random error")
    args = argparse.Namespace(device_action="list")
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to list devices: Random error")


@patch("wattweight.cli.device.DeviceManager")
def test_modify_device_success(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test modifying a device successfully."""
    mock_instance = mock_manager.return_value
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description="New Description",
        idle_timeout=600,
        idle_power=1.0,
    )
    result = device_command.execute(args)
    assert result == 0
    mock_instance.update_device.assert_called_with(
        "test",
        name="New Name",
        description="New Description",
        idle_timeout=600,
        idle_power=1.0,
    )
    logger.info.assert_called_with("Device 'test' updated successfully")


@patch("wattweight.cli.device.DeviceManager")
def test_modify_device_not_found(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test modifying a device that does not exist."""
    mock_instance = mock_manager.return_value
    mock_instance.update_device.side_effect = DeviceNotFoundError("Device not found")
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description=None,
        idle_timeout=None,
        idle_power=None,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device not found")


@patch("wattweight.cli.device.DeviceManager")
def test_modify_device_value_error(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test a value error when modifying a device."""
    mock_instance = mock_manager.return_value
    mock_instance.update_device.side_effect = ValueError("Invalid value")
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description=None,
        idle_timeout=None,
        idle_power=None,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Invalid value")


@patch("wattweight.cli.device.DeviceManager")
def test_modify_device_exception(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when modifying a device."""
    mock_instance = mock_manager.return_value
    mock_instance.update_device.side_effect = Exception("Random error")
    args = argparse.Namespace(
        device_action="modify",
        identifier="test",
        name="New Name",
        description=None,
        idle_timeout=None,
        idle_power=None,
    )
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to modify device: Random error")


@patch("wattweight.cli.device.DeviceManager")
def test_remove_device_success(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test removing a device successfully."""
    mock_instance = mock_manager.return_value
    args = argparse.Namespace(device_action="remove", identifier="test")
    result = device_command.execute(args)
    assert result == 0
    mock_instance.delete_device.assert_called_with("test")
    logger.info.assert_called_with("Device 'test' removed successfully")


@patch("wattweight.cli.device.DeviceManager")
def test_remove_device_not_found(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test removing a device that does not exist."""
    mock_instance = mock_manager.return_value
    mock_instance.delete_device.side_effect = DeviceNotFoundError("Device not found")
    args = argparse.Namespace(device_action="remove", identifier="test")
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Device not found")


@patch("wattweight.cli.device.DeviceManager")
def test_remove_device_exception(
    mock_manager, device_command: DeviceCommand, logger: Logger
):
    """Test a generic exception when removing a device."""
    mock_instance = mock_manager.return_value
    mock_instance.delete_device.side_effect = Exception("Random error")
    args = argparse.Namespace(device_action="remove", identifier="test")
    result = device_command.execute(args)
    assert result == 1
    logger.error.assert_called_with("Failed to remove device: Random error")
