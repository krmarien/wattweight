import logging
import unittest
from unittest.mock import Mock, patch

from wattweight.logger import (
    ColorFormatter,
    LogLevel,
    Logger,
    get_logger,
    set_log_level,
)


class TestLogger(unittest.TestCase):
    def tearDown(self):
        # Reset the logger singleton
        Logger._instance = None
        Logger._logger = None

    def test_singleton(self):
        logger1 = Logger()
        logger2 = Logger()
        self.assertIs(logger1, logger2)

    def test_get_logger(self):
        logger1 = get_logger()
        logger2 = get_logger()
        self.assertIs(logger1, logger2)
        self.assertIsInstance(logger1, Logger)

    def test_set_log_level(self):
        logger = get_logger()
        with patch.object(logger._logger.handlers[0], "setLevel") as mock_set_level:
            set_log_level(LogLevel.INFO)
            mock_set_level.assert_called_once_with(logging.INFO)

    @patch("logging.StreamHandler")
    def test_logger_initialization(self, mock_handler):
        """Test that the logger is initialized correctly."""
        # Force re-initialization
        Logger._instance = None
        Logger._logger = None

        logger = Logger()
        self.assertIsNotNone(logger._logger)
        self.assertEqual(logger._logger.level, logging.DEBUG)
        self.assertTrue(logger._logger.hasHandlers())

    def test_log_functions(self):
        """Test the logging functions."""
        logger = get_logger()
        with patch.object(logger._logger, "debug") as mock_debug, patch.object(
            logger._logger, "info"
        ) as mock_info, patch.object(
            logger._logger, "warning"
        ) as mock_warning, patch.object(
            logger._logger, "error"
        ) as mock_error, patch.object(
            logger._logger, "critical"
        ) as mock_critical:
            logger.debug("debug message")
            mock_debug.assert_called_once_with("debug message")

            logger.info("info message")
            mock_info.assert_called_once_with("info message")

            logger.warning("warning message")
            mock_warning.assert_called_once_with("warning message")

            logger.error("error message")
            mock_error.assert_called_once_with("error message")

            logger.critical("critical message")
            mock_critical.assert_called_once_with("critical message")


class TestColorFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = ColorFormatter()
        self.record = Mock()
        self.record.exc_info = None
        self.record.exc_text = None
        self.record.stack_info = None
        self.record.getMessage.return_value = "Test Message"

    def test_format_debug(self):
        self.record.levelno = logging.DEBUG
        self.record.levelname = "DEBUG"
        self.formatter.format(self.record)
        self.assertIn("\033[36m", self.record.levelname)
        self.assertIn("\033[0m", self.record.levelname)

    def test_format_info(self):
        self.record.levelno = logging.INFO
        self.record.levelname = "INFO"
        self.formatter.format(self.record)
        self.assertIn("\033[32m", self.record.levelname)
        self.assertIn("\033[0m", self.record.levelname)

    def test_format_warning(self):
        self.record.levelno = logging.WARNING
        self.record.levelname = "WARNING"
        self.formatter.format(self.record)
        self.assertIn("\033[33m", self.record.levelname)
        self.assertIn("\033[0m", self.record.levelname)

    def test_format_error(self):
        self.record.levelno = logging.ERROR
        self.record.levelname = "ERROR"
        self.formatter.format(self.record)
        self.assertIn("\033[31m", self.record.levelname)
        self.assertIn("\033[0m", self.record.levelname)

    def test_format_critical(self):
        self.record.levelno = logging.CRITICAL
        self.record.levelname = "CRITICAL"
        self.formatter.format(self.record)
        self.assertIn("\033[35m", self.record.levelname)
        self.assertIn("\033[0m", self.record.levelname)


if __name__ == "__main__":
    unittest.main()
