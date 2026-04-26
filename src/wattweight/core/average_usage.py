from typing import List

from sqlmodel import select

from wattweight.core.base import Core
from wattweight.model.average_usage import AverageUsage
from wattweight.model.device import Device


class AverageUsageCore(Core):
    def get_average_usage(self, device: Device) -> List[AverageUsage]:
        """Get all average usage entries for a device by its identifier."""
        average_usages = self.db.exec(
            select(AverageUsage).where(AverageUsage.device_id == device.id)
        ).all()
        return average_usages
