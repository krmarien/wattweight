"""Base manager class with shared session management."""

from typing import Optional
from sqlmodel import Session


class BaseManager:
    """Base manager class with static session management."""

    _session: Optional[Session] = None

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

    def _get_session(self) -> Session:
        """Get the shared session or create a new one.

        Returns:
            A database session
        """
        if BaseManager._session is not None:
            return BaseManager._session
        return self.db.get_session()
