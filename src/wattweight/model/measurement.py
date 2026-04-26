from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from wattweight.model.decorator.unix_timestamp import UnixTimestamp
from wattweight.model.device import Device


class Measurement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: float
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), sa_type=UnixTimestamp
    )

    # The Foreign Key
    device_id: int = Field(foreign_key="device.id")
    device: Device = Relationship(back_populates="measurements")
