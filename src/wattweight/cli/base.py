"""CLI command structure for wattweight."""

from abc import ABC, abstractmethod
import argparse
from wattweight.logger import Logger


class BaseCommand(ABC):
    """Base class for CLI commands."""

    def __init__(self):
        """Initialize the command."""
        pass

    @property
    def logger(self) -> Logger:
        """Get the logger instance."""
        return Logger()

    @classmethod
    @abstractmethod
    def register(cls, subparsers: argparse._SubParsersAction) -> None:
        """Register the command and its subcommands.

        Args:
            subparsers: The subparsers action from ArgumentParser
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the command.

        Args:
            args: Parsed command arguments

        Returns:
            Exit code
        """
