# Kim Duy Vương
# 20237410
"""Kho generic: cùng một cài đặt dùng được cho nhiều kiểu có mã định danh."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, Protocol, TypeVar, runtime_checkable

from .exceptions import DuplicateIdException
from .validation import require_text


@runtime_checkable
class IIdentifiable(Protocol):
    @property
    def id(self) -> str:
        """Mã ổn định trong suốt thời gian đối tượng được lưu trong kho."""
        ...


T = TypeVar("T", bound=IIdentifiable)


class IRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, item: T) -> None:
        ...

    @abstractmethod
    def remove(self, item_id: str) -> bool:
        ...

    @abstractmethod
    def find_by_id(self, item_id: str) -> T | None:
        ...

    @abstractmethod
    def get_all(self) -> tuple[T, ...]:
        ...

    @abstractmethod
    def find_all(self, condition: Callable[[T], bool]) -> tuple[T, ...]:
        ...


class InMemoryRepository(IRepository[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def add(self, item: T) -> None:
        if item is None:
            raise ValueError("Không được thêm None vào kho.")
        if not isinstance(item, IIdentifiable):
            raise TypeError("Đối tượng phải có thuộc tính id theo IIdentifiable.")
        item_id = require_text(item.id, "Mã đối tượng")
        if self.find_by_id(item_id) is not None:
            raise DuplicateIdException(item_id)
        self._items.append(item)

    def remove(self, item_id: str) -> bool:
        key = require_text(item_id, "Mã đối tượng")
        for index, item in enumerate(self._items):
            if item.id.strip() == key:
                del self._items[index]
                return True
        return False

    def find_by_id(self, item_id: str) -> T | None:
        key = require_text(item_id, "Mã đối tượng")
        for item in self._items:
            if item.id.strip() == key:
                return item
        return None

    def get_all(self) -> tuple[T, ...]:
        # tuple mới: không làm lộ list nội bộ, vẫn giữ đúng thứ tự thêm.
        return tuple(self._items)

    def find_all(self, condition: Callable[[T], bool]) -> tuple[T, ...]:
        if not callable(condition):
            raise TypeError("Điều kiện lọc phải là một hàm.")
        return tuple(item for item in self._items if condition(item))
