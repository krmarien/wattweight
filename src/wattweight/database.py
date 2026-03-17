"""Database initialization and management."""

import os
from pathlib import Path
from typing import Optional

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from wattweight.logger import Logger


class Database:
    """Database manager for wattweight."""

    _instance: Optional["Database"] = None
    _session_factory: Optional[scoped_session] = None
    _engine: Optional[Engine] = None

    def __new__(cls, *args, **kwargs) -> "Database":
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        in_memory: bool = False,
        db_dir: Optional[Path] = None,
        echo: bool = False,
    ):
        """Initialize the database manager.

        Args:
            in_memory: Whether to use an in-memory database (overrides db_dir)
            db_dir: Directory to store the database. If None, an in-memory database is
                used. Defaults to ~/.wattweight
            echo: Whether to echo SQL statements for debugging
        """

        if self._engine is None:
            if in_memory:
                self.database_url = "sqlite:///:memory:"
                self.db_dir = None
                self.db_path = None
            else:  # pragma: no cover
                self.db_dir = db_dir or Path(
                    os.getenv(
                        "WATTWEIGHT_DB_DIR",
                        Path.home() / ".wattweight" / "wattweight.db",
                    )
                )
                self.db_path = self.db_dir / "wattweight.db"
                self.database_url = f"sqlite:///{self.db_path}"
            self.echo = echo
            self._logger = Logger()
            _ = self.engine  # Trigger engine creation

    @property
    def engine(self) -> Engine:
        """Get or create the database engine (lazy initialization)."""
        if self._engine is None:
            self._logger.debug(f"Creating database connection: {self.database_url}")
            self._engine = create_engine(
                self.database_url,
                echo=self.echo,
                connect_args={"check_same_thread": False},
            )
        return self._engine

    def init_db(self) -> None:
        """Initialize the database, creating tables if they don't exist."""

        # Create the database directory if it doesn't exist
        if self.db_dir and not self.db_dir.exists():  # pragma: no cover
            self._logger.debug(f"Creating database directory: {self.db_dir}")
            self.db_dir.mkdir(parents=True, exist_ok=True)

        # Create all tables
        self._logger.debug("Initializing database tables")
        SQLModel.metadata.create_all(self.engine)
        self._logger.debug(f"Database initialized at {self.db_path or 'in-memory'}")

    def get_session(self) -> Session:
        """Get a database session.

        Returns:
            A shared database session for the current thread.
        """
        if self._session_factory is None:
            self._session_factory = scoped_session(
                sessionmaker(class_=Session, bind=self.engine)
            )
        session = self._session_factory()
        self._logger.debug(f"Getting database session {session}")
        return session

    def close(self) -> None:
        """Close the database connection."""
        if self._session_factory is not None:
            self._logger.debug("Removing scoped session")
            self._session_factory.remove()
            self._session_factory = None

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
