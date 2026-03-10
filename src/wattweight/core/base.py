"""Base manager class with shared session management."""

from typing import Optional
from sqlmodel import Session


class BaseManager:
    """Base manager class with static session management."""

    _session: Optional[Session] = None
    _session_owner: Optional[type] = None  # Track which class created the session

    def __init__(self, db):
        """Initialize the manager.

        Args:
            db: Database instance
        """
        self.db = db

    @classmethod
    def set_session(cls, session: Optional[Session]) -> None:
        """Set the shared session for all managers.

        Args:
            session: The session to share, or None to disable shared session
        """
        cls._session = session
        if session is None:
            cls._session_owner = None

    def _get_session(self) -> Session:
        """Get the shared session or create a new one.

        Returns:
            A database session
        """
        if BaseManager._session is not None:
            return BaseManager._session
        return self.db.get_session()

    def __enter__(self):
        """Context manager entry - creates a shared session for batch operations.

        Returns:
            The manager instance
        """
        if BaseManager._session is None:
            BaseManager._session = self.db.get_session()
            BaseManager._session_owner = self.__class__
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes the session if this instance created it."""
        if (
            BaseManager._session_owner == self.__class__
            and BaseManager._session is not None
        ):
            BaseManager._session.close()
            BaseManager._session = None
            BaseManager._session_owner = None
