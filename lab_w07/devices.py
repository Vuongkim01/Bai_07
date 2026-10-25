# Kim Duy Vương
# 20237410
"""Lớp cơ sở trừu tượng và ba loại thiết bị."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum

from .exceptions import DeviceNotReadyException
from .validation import require_percentage, require_text


class DeviceStatus(Enum):
    Available = "Available"
    Borrowed = "Borrowed"
    UnderMaintenance = "UnderMaintenance"


class TeachingDevice(ABC):
    def __init__(
        self, device_id: str, name: str, storage_location: str
    ) -> None:
        self._id = require_text(device_id, "Mã thiết bị")
        self._name = require_text(name, "Tên thiết bị")
        self._storage_location = require_text(storage_location, "Vị trí lưu trữ")
        self._status = DeviceStatus.Available

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def storage_location(self) -> str:
        return self._storage_location

    @property
    def status(self) -> DeviceStatus:
        return self._status

    @abstractmethod
    def is_ready_for_use(self) -> bool:
        """Mỗi loại thiết bị tự xác định điều kiện sẵn sàng."""

    @abstractmethod
    def get_default_priority_score(self) -> float:
        """Mỗi loại thiết bị tự tính điểm ưu tiên mặc định."""

    def borrow(self) -> None:
        # Lời gọi đa hình: thực thi is_ready_for_use của lớp con thực tế.
        if not self.is_ready_for_use():
            raise DeviceNotReadyException(self.id, self.status)
        self._status = DeviceStatus.Borrowed

    def return_device(self) -> None:
        # Không thể đặt tên hàm là return vì đây là từ khóa của Python.
        if self.status is not DeviceStatus.Borrowed:
            raise RuntimeError(f"Thiết bị '{self.id}' hiện không được mượn.")
        self._status = DeviceStatus.Available

    def __str__(self) -> str:
        return (
            f"{self.id} | {self.name} | {self.status.value} | "
            f"điểm={self.get_default_priority_score():g} | "
            f"kho={self.storage_location}"
        )


class ProjectorRemote(TeachingDevice):
    def __init__(
        self, device_id: str, name: str, storage_location: str, battery_level: int
    ) -> None:
        super().__init__(device_id, name, storage_location)
        self._battery_level = require_percentage(battery_level, "Mức pin")

    @property
    def battery_level(self) -> int:
        return self._battery_level

    def is_ready_for_use(self) -> bool:
        return self.status is DeviceStatus.Available and self.battery_level >= 20

    def get_default_priority_score(self) -> float:
        return float(self.battery_level)


class AirConditionerRemote(TeachingDevice):
    def __init__(
        self,
        device_id: str,
        name: str,
        storage_location: str,
        compatible_rooms: Iterable[str],
    ) -> None:
        super().__init__(device_id, name, storage_location)
        if compatible_rooms is None or isinstance(compatible_rooms, (str, bytes)):
            raise TypeError("Phòng tương thích phải là một tập hợp các mã phòng.")
        self._compatible_rooms = frozenset(
            require_text(room, "Mã phòng") for room in compatible_rooms
        )

    @property
    def compatible_rooms(self) -> frozenset[str]:
        return self._compatible_rooms

    def is_compatible_with(self, room_id: str) -> bool:
        return require_text(room_id, "Mã phòng") in self.compatible_rooms

    def is_ready_for_use(self) -> bool:
        return self.status is DeviceStatus.Available

    def get_default_priority_score(self) -> float:
        # Không có tham số phòng trong chữ ký gốc; xem quyết định ở DESIGN.md.
        return 100.0 if self.compatible_rooms else 0.0

    def get_priority_score_for_room(self, room_id: str) -> float:
        return 100.0 if self.is_compatible_with(room_id) else 0.0


class WirelessMicrophone(TeachingDevice):
    def __init__(
        self,
        device_id: str,
        name: str,
        storage_location: str,
        battery_level: int,
        signal_quality: int,
    ) -> None:
        super().__init__(device_id, name, storage_location)
        self._battery_level = require_percentage(battery_level, "Mức pin")
        self._signal_quality = require_percentage(signal_quality, "Chất lượng tín hiệu")

    @property
    def battery_level(self) -> int:
        return self._battery_level

    @property
    def signal_quality(self) -> int:
        return self._signal_quality

    def is_ready_for_use(self) -> bool:
        return (
            self.status is DeviceStatus.Available
            and self.battery_level >= 30
            and self.signal_quality >= 40
        )

    def get_default_priority_score(self) -> float:
        return (self.battery_level + self.signal_quality) / 2
