"""Đồng hồ ảo: mọi dịch vụ đọc 'giờ ảo' thay vì giờ máy.

speed = 1    -> thời gian ảo chạy bằng thời gian thật
speed = 1440 -> 1 ngày ảo trôi qua trong 1 phút thật
"""

import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta


class VirtualClock:
    def __init__(
        self,
        start: datetime,
        speed: float = 1.0,
        real_time: Callable[[], float] = time.monotonic,
    ) -> None:
        if speed <= 0:
            raise ValueError("speed phải > 0")
        if start.tzinfo is None:
            start = start.replace(tzinfo=UTC)
        self._start = start
        self._speed = speed
        self._real_time = real_time
        self._t0 = real_time()

    @property
    def speed(self) -> float:
        return self._speed

    def now(self) -> datetime:
        elapsed_real = self._real_time() - self._t0
        return self._start + timedelta(seconds=elapsed_real * self._speed)
