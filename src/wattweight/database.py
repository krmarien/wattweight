"""Database initialization and management."""

import os
from pathlib import Path
from typing import Optional

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import Engine

from wattweight.logger import get_logger


class Database:
    """Database manager for wattweight."""

    def __init__(
        self,
        db_dir: Optional[Path] = None,
        echo: bool = False,
    ):
        """Initialize the database manager.

        Args:
            db_dir: Directory to store the database. Defaults to ~/.wattweight
            echo: Whether to echo SQL statements for debugging
        """
        self.db_dir = db_dir or Path(os.getenv("WATTWEIGHT_DB_DIR", Path.cwd() / ".wattweight"))
        self.db_path = self.db_dir / "wattweight.db"
        self.database_url = f"sqlite:///{self.db_path}"
        self.echo = echo
        self._engine: Optional[Engine] = None
        self._logger = get_logger()

    @property
    def engine(self) -> Engine:
        """Get or create the database engine (lazy initialization)."""
        if self._engine is None:
            self._logger.debug(f"Creating database connection: {self.db_path}")
            self._engine = create_engine(
                self.database_url,
                echo=self.echo,
                connect_args={"check_same_thread": False},
            )
        return self._engine

    def init_db(self) -> None:
        """Initialize the database, creating tables if they don't exist."""
        # Import models here to ensure they're registered with SQLModel
        from wattweight.model import Device  # noqa: F401

        # Create the database directory if it doesn't exist
        if not self.db_dir.exists():
            self._logger.debug(f"Creating database directory: {self.db_dir}")
            self.db_dir.mkdir(parents=True, exist_ok=True)

        # Create all tables
        self._logger.debug("Initializing database tables")
        SQLModel.metadata.create_all(self.engine)
        self._logger.debug(f"Database initialized at {self.db_path}")

    def get_session(self) -> Session:
        """Get a database session.

        Returns:
            A new database session
        """
        self._logger.debug("Creating new database session")
        return Session(self.engine)

    def close(self) -> None:
        """Close the database connection."""
        if self._engine is not None:
            self._logger.debug("Closing database connection")
            self._engine.dispose()
            self._engine = None

    def __enter__(self) -> "Database":
        """Context manager entry."""
        self.init_db()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Context manager exit."""
        self.close()

