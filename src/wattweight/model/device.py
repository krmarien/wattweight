from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:  # pragma: no cover
    from .measurement import Measurement  # Only imported for type hints


class DeviceState(str, Enum):
    UNKNOWN = "unknown"
    READY = "ready"


class DeviceMeasuringState(str, Enum):
    MEASURING = "measuring"
    NOT_MEASURING = "not_measuring"


class DeviceMeasurementUnit(str, Enum):
    WATTS = "watts"
    WATT_HOURS = "watt_hours"


class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    identifier: str = Field(index=True)
    name: str
    description: Optional[str] = None
    idle_timeout: int = 20 * 60  # Default idle timeout in seconds (20 minutes)
    idle_energy_threshold: float = 2.0  # Power consumption when idle (in watthours)
    measurement_unit: DeviceMeasurementUnit = DeviceMeasurementUnit.WATT_HOURS
    state: DeviceState = DeviceState.UNKNOWN
    measuring_state: DeviceMeasuringState = DeviceMeasuringState.NOT_MEASURING

    measurements: List["Measurement"] = Relationship(back_populates="device")
