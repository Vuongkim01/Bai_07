# Kim Duy Vương
# 20237410
"""Các ngoại lệ nghiệp vụ được yêu cầu."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .devices import DeviceStatus


class DuplicateIdException(Exception):
    def __init__(self, duplicate_id: str) -> None:
        self.duplicate_id = duplicate_id
        super().__init__(f"Mã '{duplicate_id}' đã tồn tại trong kho.")


class NoSuitableItemException(Exception):
    def __init__(self) -> None:
        super().__init__("Không có ứng viên phù hợp để lựa chọn.")


class DeviceNotReadyException(Exception):
    def __init__(self, device_id: str, current_status: DeviceStatus) -> None:
        self.device_id = device_id
        self.current_status = current_status
        super().__init__(
            f"Thiết bị '{device_id}' chưa sẵn sàng để mượn "
            f"(trạng thái: {current_status.value})."
        )
