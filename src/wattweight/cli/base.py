"""CLI command structure for wattweight."""

from abc import ABC, abstractmethod
import argparse
from wattweight.database import Database
from wattweight.logger import Logger


class BaseCommand(ABC):
    """Base class for CLI commands."""

    def __init__(self, db: Database, logger: Logger):
        """Initialize the command.

        Args:
            db: Database instance
            logger: Logger instance
        """
        self.db = db
        self.logger = logger

    @abstractmethod
    def register(self, subparsers: argparse._SubParsersAction) -> None:
        """Register command and subcommands with argparse.

        Args:
            subparsers: The subparsers action from ArgumentParser
        """

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the command.

        Args:
            args: Parsed command arguments

        Returns:
            Exit code
        """
