"""Logging module with color support for wattweight."""

import logging
from enum import Enum
from typing import Optional, Any


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColorFormatter(logging.Formatter):
    """Formatter with color support for terminal output."""

    # ANSI color codes
    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow/Orange
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Get the color for this log level
        color = self.COLORS.get(record.levelno, "")

        # Format the message
        if color:
            # Colorize the level name
            record.levelname = f"{color}{record.levelname}{self.RESET}"

        # Use the default formatting
        return super().format(record)


class Logger:
    """Logger for wattweight with color support."""

    _instance: Optional["Logger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> "Logger":
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger."""
        if self._logger is None:
            self._logger = logging.getLogger("wattweight")
            self._logger.setLevel(
                logging.DEBUG
            )  # Accept all messages, filter at handler level

            # Only add handler if not already present
            if not self._logger.handlers:
                handler = logging.StreamHandler()
                formatter = ColorFormatter(fmt="[%(levelname)s] %(message)s")
                handler.setFormatter(formatter)
                self._logger.addHandler(handler)

    def set_level(self, level: LogLevel) -> None:
        """Set the logging level.

        Args:
            level: The LogLevel to set
        """
        if self._logger is not None:
            for handler in self._logger.handlers:
                handler.setLevel(level.value)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        if self._logger is not None:
            self._logger.debug(message)

    def info(self, message: str) -> None:
        """Log an info message."""
        if self._logger is not None:
            self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        if self._logger is not None:
            self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        if self._logger is not None:
            self._logger.error(message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        if self._logger is not None:
            self._logger.critical(message)
