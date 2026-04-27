from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, TypeDecorator
from sqlalchemy.engine.interfaces import Dialect


class UnixTimestamp(TypeDecorator[datetime]):
    """Stores Python datetime objects as Unix timestamps (integers) in SQLite."""

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: object, dialect: Dialect) -> Optional[int]:
        if value is None:  # pragma: no cover
            return value

        # If filtering with an int directly, just return it
        if isinstance(value, int):  # pragma: no cover
            return value

        # If it's a datetime object, convert it to an int
        if isinstance(value, datetime):
            return int(value.timestamp())

        raise TypeError(
            f"Expected datetime or int, got {type(value)}"
        )  # pragma: no cover

    def process_result_value(
        self, value: object, dialect: Dialect
    ) -> Optional[datetime]:
        if isinstance(value, (int)):
            # Convert integer timestamp from DB back to datetime object
            return datetime.fromtimestamp(value, tz=timezone.utc)
        return None  # pragma: no cover
