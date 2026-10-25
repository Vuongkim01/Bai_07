# Kim Duy Vương
# 20237410
"""Dịch vụ cấp phát generic; không kiểm tra loại thiết bị cụ thể."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from .devices import TeachingDevice
from .repository import IRepository
from .strategies import ISelectionStrategy

D = TypeVar("D", bound=TeachingDevice)


class AllocationService(Generic[D]):
    def __init__(
        self, repository: IRepository[D], strategy: ISelectionStrategy[D]
    ) -> None:
        if repository is None:
            raise ValueError("Repository không được là None.")
        if strategy is None:
            raise ValueError("Strategy không được là None.")
        self._repository = repository
        self._strategy = strategy

    def change_strategy(self, new_strategy: ISelectionStrategy[D]) -> None:
        if new_strategy is None:
            raise ValueError("Strategy không được là None.")
        self._strategy = new_strategy

    def allocate(self, additional_condition: Callable[[D], bool] | None = None) -> D:
        if additional_condition is not None and not callable(additional_condition):
            raise TypeError("Điều kiện bổ sung phải là một hàm hoặc None.")

        candidates = tuple(
            device
            for device in self._repository.get_all()
            if device.is_ready_for_use()
            and (additional_condition is None or additional_condition(device))
        )
        selected = self._strategy.select(candidates)
        selected.borrow()
        return selected
