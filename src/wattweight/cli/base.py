"""CLI command structure for wattweight."""

from abc import ABC, abstractmethod
import argparse
from wattweight.database import Database
from wattweight.logger import Logger, get_logger


class BaseCommand(ABC):
    """Base class for CLI commands."""

    def __init__(self, db: Database):
        """Initialize the command.

        Args:
            db: Database instance
        """
        self.db = db

    @property
    def logger(self) -> Logger:
        """Get the logger instance."""
        return get_logger()

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the command.

        Args:
            args: Parsed command arguments

        Returns:
            Exit code
        """
