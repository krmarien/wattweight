import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from wattweight.core.migration import MigrationManager


class TestMigrationManager(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_db.database_url = "sqlite:///:memory:"
        self.manager = MigrationManager(self.mock_db)
        self.alembic_ini_path = (Path(__file__).parent.parent / "alembic.ini").resolve()

    @patch("subprocess.run")
    def test_upgrade_success(self, mock_subprocess_run):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Upgrade successful"
        mock_subprocess_run.return_value = mock_process

        result = self.manager.upgrade()

        self.assertTrue(result)
        expected_command = [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(self.alembic_ini_path),
            "upgrade",
            "head",
        ]
        mock_subprocess_run.assert_called_once()
        called_args = mock_subprocess_run.call_args[0][0]
        self.assertEqual(called_args, expected_command)
        called_env = mock_subprocess_run.call_args[1]["env"]
        self.assertEqual(called_env["SQLALCHEMY_URL"], self.mock_db.database_url)

    @patch("subprocess.run")
    def test_upgrade_failure(self, mock_subprocess_run):
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = "Upgrade failed"
        mock_subprocess_run.return_value = mock_process

        with self.assertRaises(RuntimeError) as context:
            self.manager.upgrade()
        self.assertIn("Migration failed", str(context.exception))

    def test_upgrade_exception(self):
        with patch("subprocess.run", side_effect=Exception("Test exception")):
            with self.assertRaises(RuntimeError) as context:
                self.manager.upgrade()
            self.assertIn("Failed to upgrade database", str(context.exception))

    @patch("subprocess.run")
    def test_create_migration_success(self, mock_subprocess_run):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Migration created"
        mock_subprocess_run.return_value = mock_process

        message = "test migration"
        result = self.manager.create_migration(message)

        self.assertTrue(result)
        expected_command = [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(self.alembic_ini_path),
            "revision",
            "--autogenerate",
            "-m",
            message,
        ]
        mock_subprocess_run.assert_called_once()
        called_args = mock_subprocess_run.call_args[0][0]
        self.assertEqual(called_args, expected_command)
        called_env = mock_subprocess_run.call_args[1]["env"]
        self.assertEqual(called_env["SQLALCHEMY_URL"], self.mock_db.database_url)

    @patch("subprocess.run")
    def test_create_migration_failure(self, mock_subprocess_run):
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = "Migration creation failed"
        mock_subprocess_run.return_value = mock_process

        with self.assertRaises(RuntimeError) as context:
            self.manager.create_migration("test migration")
        self.assertIn("Migration creation failed", str(context.exception))

    def test_create_migration_exception(self):
        with patch("subprocess.run", side_effect=Exception("Test exception")):
            with self.assertRaises(RuntimeError) as context:
                self.manager.create_migration("test migration")
            self.assertIn("Failed to create migration", str(context.exception))


if __name__ == "__main__":
    unittest.main()
