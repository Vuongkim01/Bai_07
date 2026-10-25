# Kim Duy Vương
# 20237410
"""Đa hình hóa thuật toán lựa chọn; không phụ thuộc loại thiết bị."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Generic, TypeVar

from .exceptions import NoSuitableItemException

S = TypeVar("S")


class ISelectionStrategy(ABC, Generic[S]):
    @abstractmethod
    def select(self, candidates: Sequence[S]) -> S:
        ...


class HighestPriorityStrategy(ISelectionStrategy[S]):
    def __init__(self, score_selector: Callable[[S], float]) -> None:
        if not callable(score_selector):
            raise TypeError("Hàm tính điểm phải là một hàm có thể gọi.")
        self._score_selector = score_selector

    def select(self, candidates: Sequence[S]) -> S:
        if not candidates:
            raise NoSuitableItemException()
        # max không sắp xếp/sửa đầu vào; điểm bằng nhau giữ phần tử đầu tiên.
        return max(candidates, key=self._score_selector)


class FirstAvailableStrategy(ISelectionStrategy[S]):
    def select(self, candidates: Sequence[S]) -> S:
        if not candidates:
            raise NoSuitableItemException()
        # Service đã lọc sẵn sàng; strategy chỉ cần chọn ứng viên đầu tiên.
        return candidates[0]
