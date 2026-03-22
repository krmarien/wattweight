"""Device State Service core business logic."""

from datetime import timezone, datetime
import pandas as pd

from sqlmodel import select

from wattweight.database import Database
from wattweight.model.measurement import Measurement
from wattweight.logger import Logger
from wattweight.model.device import Device, DeviceMeasuringState, DeviceMeasurementUnit


class DeviceStateService:
    @staticmethod
    def update_state(device: Device):
        """Update the state of a device based on its last measurement time and idle
            timeout.

        Args:
            device: The device to update
        """

        logger = Logger()
        db = Database().get_session()

        if len(device.measurements) == 0:
            logger.debug(
                f"Device {device.identifier} has no measurements, skipping state"
                "update."
            )
            return

        # Detect if device is idle based on last measurement time and idle timeout
        device_idle = DeviceStateService.is_device_idle(device)

        if not device_idle:
            device.measuring_state = DeviceMeasuringState.MEASURING
            logger.debug(
                f"Device {device.identifier} is not idle, skipping state update."
            )
            return

        # Update device average power
        # TODO

        # Remove all measurements for this device
        for measurement in device.measurements:
            db.delete(measurement)

        device.measuring_state = DeviceMeasuringState.NOT_MEASURING
        db.commit()

    @staticmethod
    def is_device_idle(device: Device):
        db = Database().get_session()
        logger = Logger()

        # Get measurements for this device in the last device.idle_timeout seconds
        # and check the are about the device.idle_threshold
        idle_measurements = db.exec(
            select(Measurement)
            .where(
                Measurement.device_id == device.id,
                Measurement.timestamp
                > int(datetime.now(timezone.utc).timestamp()) - device.idle_timeout,
            )
            .order_by(Measurement.timestamp.asc())
        ).all()

        _ = DeviceStateService.get_energy_for_measurements(device, idle_measurements)

        if len(idle_measurements) > 0:
            above_threshold = [
                m for m in idle_measurements if m.value > device.idle_energy_threshold
            ]
            logger.debug(
                f"Device {device.identifier} has {len(above_threshold)} measurements"
                f"above the idle threshold in the last {device.idle_timeout} seconds."
            )
            return len(above_threshold) == 0
        else:
            logger.debug(
                f"No measurements found for device {device.identifier} in the last"
                f"{device.idle_timeout} seconds."
            )
            return True

    @staticmethod
    def get_energy_for_measurements(device: Device, measurements: list[Measurement]):
        if device.measurement_unit == DeviceMeasurementUnit.WATTS:
            # 1. Convert your list of SQLModel objects to a list of dictionaries
            data = [m.model_dump() for m in measurements]
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
            df = df.sort_values("timestamp")

            # 2. Calculate the time gap between readings in hours
            # .diff() gives a Timedelta; .dt.total_seconds() / 3600 converts to hours
            df["hours_passed"] = df["timestamp"].diff().dt.total_seconds() / 3600

            # 3. Calculate Average Power for the interval
            # Average the Power (W) of the current and previous reading
            df["avg_power"] = (df["value"] + df["value"].shift(1)) / 2

            # 4. Energy (Wh) = Power (W) * Time (h)
            df["energy_delta"] = df["avg_power"] * df["hours_passed"]

            # Because the first entry of a diff() is always NaN,
            # we drop it and return the rest as a list of energy deltas.
            return df["energy_delta"].dropna().tolist()
        else:
            # 1. Convert your list of SQLModel objects to a list of dictionaries
            data = [m.model_dump() for m in measurements]
            df = pd.DataFrame(data)

            # 2. Convert Unix integer to readable Datetime
            # unit='s' if it's seconds, 'ms' if milliseconds
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)

            # 3. Sort to ensure chronological order
            df = df.sort_values("timestamp")

            # 4. Calculate the energy per timestep (delta)
            df["energy_delta"] = df["value"].diff()

            # Because the first entry of a diff() is always NaN,
            # we drop it and return the rest as a list of energy deltas.
            return df["energy_delta"].dropna().tolist()
