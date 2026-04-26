"""Database migration management."""

import os
import subprocess
import sys
from pathlib import Path

from wattweight.core.base import Core
from wattweight.database import Database


class MigrationCore(Core):
    """Core class for database migrations using Alembic."""

    alembic_ini = Path(__file__).parent.parent.parent.parent / "alembic.ini"

    def upgrade(self) -> bool:
        """Upgrade the database to the latest version.

        Returns:
            True if successful, False otherwise
        """
        try:
            env = os.environ.copy()
            env["SQLALCHEMY_URL"] = Database().database_url

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "alembic",
                    "-c",
                    str(self.alembic_ini),
                    "upgrade",
                    "head",
                ],
                cwd=str(self.alembic_ini.parent),
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Migration failed: {e.stdout}\\n{e.stderr}") from e

    def create_migration(self, message: str) -> None:
        """Create a new migration.

        Args:
            message: Migration message/description

        Returns:
            True if successful, False otherwise
        """
        try:
            env = os.environ.copy()
            env["SQLALCHEMY_URL"] = Database().database_url

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "alembic",
                    "-c",
                    str(self.alembic_ini),
                    "revision",
                    "--autogenerate",
                    "-m",
                    message,
                ],
                cwd=str(self.alembic_ini.parent),
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"Migration created: {result.stdout}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Migration creation failed: {e.stdout}\n{e.stderr}"
            ) from e
