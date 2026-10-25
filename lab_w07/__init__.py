# Kim Duy Vương
# 20237410
"""Lab W07: quản lý thiết bị bằng đa hình và generic."""

from .devices import (
    AirConditionerRemote,
    DeviceStatus,
    ProjectorRemote,
    TeachingDevice,
    WirelessMicrophone,
)
from .exceptions import (
    DeviceNotReadyException,
    DuplicateIdException,
    NoSuitableItemException,
)
from .repository import IIdentifiable, InMemoryRepository, IRepository
from .service import AllocationService
from .strategies import (
    FirstAvailableStrategy,
    HighestPriorityStrategy,
    ISelectionStrategy,
)

__all__ = [
    "AirConditionerRemote", "AllocationService", "DeviceNotReadyException",
    "DeviceStatus", "DuplicateIdException", "FirstAvailableStrategy",
    "HighestPriorityStrategy", "IIdentifiable", "InMemoryRepository",
    "IRepository", "ISelectionStrategy", "NoSuitableItemException",
    "ProjectorRemote", "TeachingDevice", "WirelessMicrophone",
]
