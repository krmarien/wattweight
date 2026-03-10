from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING: # pragma: no cover
    from .measurement import Measurement # Only imported for type hints

class DeviceState(str, Enum):
    UNKNOWN = "unknown"
    READY = "ready"

class DeviceMeasuringState(str, Enum):
    UNKNOWN = "unknown"
    MEASURING = "measuring"
    IDLE = "idle"


class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    identifier: str = Field(index=True)
    name: str
    description: Optional[str] = None
    idle_timeout: int = 20*60  # Default idle timeout in seconds (20 minutes)
    idle_power: float = 2.0  # Power consumption when idle (in watts)
    state: DeviceState = DeviceState.UNKNOWN
    measuring_state: DeviceMeasuringState = DeviceMeasuringState.UNKNOWN

    measurements: List["Measurement"] = Relationship(back_populates="device")

