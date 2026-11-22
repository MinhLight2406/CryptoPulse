from datetime import UTC, datetime

import pytest
from cryptopulse_common import VirtualClock, topics


class FakeTime:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def test_clock_runs_faster_than_real_time():
    fake = FakeTime()
    start = datetime(2024, 1, 1, tzinfo=UTC)
    clock = VirtualClock(start, speed=1440, real_time=fake)
    fake.t += 60  # 1 phút thật
    assert (clock.now() - start).total_seconds() == 86400  # 1 ngày ảo


def test_clock_rejects_invalid_speed():
    with pytest.raises(ValueError):
        VirtualClock(datetime(2024, 1, 1, tzinfo=UTC), speed=0)


def test_topics_are_unique():
    assert len(topics.ALL) == len(set(topics.ALL))
