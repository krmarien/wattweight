from datetime import datetime, timezone

from sqlalchemy import Integer, TypeDecorator


class UnixTimestamp(TypeDecorator):
    """Stores Python datetime objects as Unix timestamps (integers) in SQLite."""

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:  # pragma: no cover
            return value

        # If filtering with an int directly, just return it
        if isinstance(value, int):
            return value

        # If it's a datetime object, convert it to an int
        if isinstance(value, datetime):
            return int(value.timestamp())

        raise TypeError(
            f"Expected datetime or int, got {type(value)}"
        )  # pragma: no cover

    def process_result_value(self, value, dialect):
        if value is not None:
            # Convert integer timestamp from DB back to datetime object
            return datetime.fromtimestamp(value, tz=timezone.utc)
        return value  # pragma: no cover
