"""Lõi phát lại: gộp nhiều chuỗi nến theo thời gian và điều tiết theo đồng hồ ảo."""

import heapq
import time
from collections.abc import Callable, Iterable, Iterator

from .clock import VirtualClock
from .events import CandleEvent


def merge_by_time(streams: Iterable[Iterable[CandleEvent]]) -> Iterator[CandleEvent]:
    """Gộp các chuỗi (mỗi chuỗi đã sắp theo thời gian) thành một chuỗi duy nhất.

    Thứ tự xác định: theo `available_at`, nếu trùng thì theo tên symbol.
    """
    return heapq.merge(*streams, key=lambda e: (e.available_at, e.symbol))


def paced(
    events: Iterable[CandleEvent],
    clock: VirtualClock,
    sleep: Callable[[float], None] = time.sleep,
    max_nap: float = 0.5,
) -> Iterator[CandleEvent]:
    """Chỉ phát sự kiện khi đồng hồ ảo đã đi tới `available_at` của nó."""
    for ev in events:
        due = ev.available_at / 1000
        while True:
            remaining = due - clock.now().timestamp()
            if remaining <= 0:
                break
            sleep(min(remaining / clock.speed, max_nap))
        yield ev
