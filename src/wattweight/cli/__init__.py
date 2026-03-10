"""CLI module for wattweight."""

from wattweight.cli.base import BaseCommand
from wattweight.cli.device import DeviceCommand
from wattweight.cli.measurement import MeasurementCommand
from wattweight.cli.upgrade import UpgradeCommand

__all__ = ["BaseCommand", "DeviceCommand", "MeasurementCommand", "UpgradeCommand"]
