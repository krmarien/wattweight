"""Database migration management."""

import os
from pathlib import Path
import subprocess
import sys

from wattweight.database import Database


class MigrationManager:
    """Manager for database migrations using Alembic."""

    def __init__(self, db: Database):
        """Initialize the migration manager.

        Args:
            db: Database instance
        """
        self.db = db
        self.alembic_ini = Path(__file__).parent.parent.parent.parent / "alembic.ini"

    def upgrade(self) -> bool:
        """Upgrade the database to the latest version.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Set environment variable for alembic to find the database
            env = os.environ.copy()
            env["SQLALCHEMY_URL"] = self.db.database_url
            print(env["SQLALCHEMY_URL"])

            # Run alembic upgrade head
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "alembic",
                    "-c",
                    str(self.alembic_ini),
                    "upgrade",
                    "head",
                ],
                cwd=str(Path(__file__).parent.parent.parent.parent),
                env=env,
                capture_output=True,
                text=True,
            )
            print([
                    sys.executable,
                    "-m",
                    "alembic",
                    "-c",
                    str(self.alembic_ini),
                    "upgrade",
                    "head",
                ])

            if result.returncode != 0:
                raise RuntimeError(f"Migration failed: {result.stdout}")

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to upgrade database: {str(e)}")

    def create_migration(self, message: str) -> bool:
        """Create a new migration.

        Args:
            message: Migration message/description

        Returns:
            True if successful, False otherwise
        """
        try:
            env = os.environ.copy()
            env["SQLALCHEMY_URL"] = self.db.database_url

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
                cwd=str(Path(__file__).parent.parent.parent.parent),
                env=env,
                capture_output=True,
                text=True,
            )
            print(" ".join([
                    sys.executable,
                    "-m",
                    "alembic",
                    "-c",
                    str(self.alembic_ini),
                    "revision",
                    "--autogenerate",
                    "-m",
                    message,
                ]))

            if result.returncode != 0:
                raise RuntimeError(f"Migration creation failed: {result.stdout}")

            print(f"Migration created: {result.stdout}")
            return True

        except Exception as e:
            raise RuntimeError(f"Failed to create migration: {str(e)}")
