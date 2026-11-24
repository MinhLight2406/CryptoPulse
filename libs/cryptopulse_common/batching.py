"""Bộ đệm gom sự kiện thành lô: đủ số lượng hoặc đủ tuổi thì xả."""

import time
from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class BatchBuffer(Generic[T]):
    def __init__(
        self,
        max_size: int,
        max_age: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_size < 1:
            raise ValueError("max_size phải >= 1")
        self._max_size = max_size
        self._max_age = max_age
        self._clock = clock
        self._items: list[T] = []
        self._first_at = 0.0

    def __len__(self) -> int:
        return len(self._items)

    def add(self, item: T) -> None:
        if not self._items:
            self._first_at = self._clock()
        self._items.append(item)

    def ready(self) -> bool:
        if not self._items:
            return False
        if len(self._items) >= self._max_size:
            return True
        return self._clock() - self._first_at >= self._max_age

    def drain(self) -> list[T]:
        items, self._items = self._items, []
        return items
