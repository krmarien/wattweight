from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from wattweight.model.device import Device


class AverageUsage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: int
    value: float

    # The Foreign Key
    device_id: int = Field(foreign_key="device.id")
    device: Device = Relationship(back_populates="average_usage")
