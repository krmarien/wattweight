"""Models for the wattweight database."""

from wattweight.model.average_usage import AverageUsage
from wattweight.model.device import Device
from wattweight.model.measurement import Measurement

__all__ = ["Device", "Measurement", "AverageUsage"]
