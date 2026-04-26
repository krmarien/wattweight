"""Device State Service core business logic."""

from datetime import datetime, timezone
from itertools import zip_longest
from typing import Sequence

import pandas as pd
from sqlmodel import asc, desc, select

from wattweight.database import Database
from wattweight.logger import Logger
from wattweight.model.average_usage import AverageUsage
from wattweight.model.device import Device, DeviceMeasurementUnit, DeviceMeasuringState
from wattweight.model.measurement import Measurement


class DeviceStateService:
    SAMPLE_FREQUENCY_MINUTES = 5
    AVERAGE_USAGE_WEIGHT = 0.9

    @staticmethod
    def update_state(device: Device) -> None:
        """Update the state of a device based on its last measurement time and idle
            timeout.

        Args:
            device: The device to update
        """

        logger = Logger()
        db = Database().get_session()

        if len(device.measurements) == 0:  # pragma: no cover
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

        # Update device average energy
        DeviceStateService.update_average_energy(device)

        # Remove all measurements for this device
        for measurement in device.measurements:
            db.delete(measurement)

        device.measuring_state = DeviceMeasuringState.NOT_MEASURING
        db.add(device)
        db.commit()

    @staticmethod
    def is_device_idle(device: Device) -> bool:
        db = Database().get_session()
        logger = Logger()

        threshold_dt = datetime.fromtimestamp(
            int(datetime.now(timezone.utc).timestamp()) - device.idle_timeout,
            tz=timezone.utc,
        )

        # Get measurements for this device in the last device.idle_timeout seconds
        # and check the are about the device.idle_threshold
        idle_measurements = db.exec(
            select(Measurement)
            .where(
                Measurement.device_id == device.id,
                Measurement.timestamp > threshold_dt,
            )
            .order_by(asc(Measurement.timestamp))
        ).all()

        energy = DeviceStateService.get_energy_for_measurements(
            device, idle_measurements
        )

        if len(idle_measurements) == 1:
            logger.debug(
                f"Device {device.identifier} has only one measurement in the last"
                f"{device.idle_timeout} seconds, treating as not idle."
            )
            return False
        elif len(idle_measurements) > 1:
            above_threshold = [
                m for m in energy if m["value"] > device.idle_energy_threshold
            ]
            logger.debug(
                f"Device {device.identifier} has {len(above_threshold)} measurements"
                f"above the idle threshold in the last {device.idle_timeout} seconds."
            )
            return len(above_threshold) == 0
        else:  # pragma: no cover
            logger.debug(
                f"No measurements found for device {device.identifier} in the last"
                f"{device.idle_timeout} seconds."
            )
            return True

    @staticmethod
    def update_average_energy(device: Device) -> None:
        db = Database().get_session()
        logger = Logger()

        # Get all the measurements for this device
        measurements = db.exec(
            select(Measurement)
            .where(Measurement.device_id == device.id)
            .order_by(asc(Measurement.timestamp))
        ).all()

        logger.debug(
            f"Device {device.identifier} has {len(measurements)} measurement in total"
        )

        energy = DeviceStateService.get_energy_for_measurements(device, measurements)

        # Get current average usage for this device
        current_average_usage = db.exec(
            select(AverageUsage)
            .where(
                AverageUsage.device_id == device.id,
            )
            .order_by(desc(AverageUsage.timestamp))
        ).all()

        for energy_entry, average_usage_entry in zip_longest(
            energy, current_average_usage
        ):
            if average_usage_entry is not None and energy_entry is not None:
                # Update existing average usage entry
                average_usage_entry.value = (
                    average_usage_entry.value * DeviceStateService.AVERAGE_USAGE_WEIGHT
                    + energy_entry["value"]
                    * (1 - DeviceStateService.AVERAGE_USAGE_WEIGHT)
                )
                db.add(average_usage_entry)
            elif energy_entry is not None:
                # Create new average usage entry
                average_usage = AverageUsage(
                    device_id=device.id,
                    timestamp=energy_entry["timestamp"],
                    value=energy_entry["value"],
                )
                db.add(average_usage)

        db.commit()

    @staticmethod
    def get_energy_for_measurements(
        device: Device, measurements: Sequence[Measurement]
    ) -> list[dict[str, int | float]]:
        if not measurements:
            return []  # pragma: no cover

        # 1. Convert list of SQLModel objects to a list of dictionaries
        data = [m.model_dump() for m in measurements]
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
        df = df.sort_values("timestamp")

        if device.measurement_unit == DeviceMeasurementUnit.WATTS:
            # Calculate cumulative energy from power using trapezoidal rule
            df["hours_passed"] = df["timestamp"].diff().dt.total_seconds() / 3600
            df["avg_power"] = (df["value"] + df["value"].shift(1)) / 2
            df["energy_segment"] = df["avg_power"] * df["hours_passed"]
            df["cumulative_energy"] = df["energy_segment"].fillna(0).cumsum()
        else:
            # WATT_HOURS is already cumulative
            df["cumulative_energy"] = df["value"]

        # 2. Resample cumulative energy to 5-minute intervals
        df = df.set_index("timestamp")
        # Handle duplicate timestamps by keeping the first
        df = df[~df.index.duplicated(keep="first")]

        if df.empty:
            return []  # pragma: no cover

        # Define the target 5-minute grid
        start = df.index.min()
        end = df.index.max().ceil(f"{DeviceStateService.SAMPLE_FREQUENCY_MINUTES}min")
        grid = pd.date_range(
            start=start,
            end=end,
            freq=f"{DeviceStateService.SAMPLE_FREQUENCY_MINUTES}min",
        )

        # Combine original timestamps with grid
        combined_index = df.index.union(grid).sort_values()

        # Reindex and interpolate cumulative energy
        cumulative = (
            df["cumulative_energy"].reindex(combined_index).interpolate(method="time")
        )

        # Fill boundaries to cover the full grid
        cumulative = cumulative.bfill().ffill()

        # Select only the grid points and calculate diff
        resampled = cumulative.loc[grid]
        energy_intervals = resampled.diff().dropna()

        # Return as list of dictionaries with interval start time
        result = []
        start_time = df.index.min()
        for ts, value in energy_intervals.items():
            if not isinstance(ts, pd.Timestamp):
                raise TypeError(
                    f"Expected timestamp to be a pd.Timestamp, got {type(ts)}"
                )

            result.append(
                {
                    "timestamp": int(
                        (
                            ts
                            - pd.Timedelta(
                                minutes=DeviceStateService.SAMPLE_FREQUENCY_MINUTES
                            )
                            - start_time
                        ).total_seconds()
                    ),
                    "value": value,
                }
            )

        return result
