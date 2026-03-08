from typing import Optional
from sqlmodel import Field, SQLModel
from enum import Enum

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
