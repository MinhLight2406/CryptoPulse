import pytest
from cryptopulse_common.batching import BatchBuffer


class FakeTime:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def test_ready_when_size_reached():
    buf = BatchBuffer(max_size=3, max_age=100, clock=FakeTime())
    buf.add(1)
    buf.add(2)
    assert not buf.ready()
    buf.add(3)
    assert buf.ready()


def test_ready_when_old_enough():
    clock = FakeTime()
    buf = BatchBuffer(max_size=1000, max_age=1.0, clock=clock)
    buf.add("a")
    clock.t = 0.5
    assert not buf.ready()
    clock.t = 1.0
    assert buf.ready()


def test_empty_buffer_is_never_ready():
    clock = FakeTime()
    buf = BatchBuffer(max_size=1, max_age=0.0, clock=clock)
    clock.t = 999
    assert not buf.ready()


def test_drain_returns_items_and_resets():
    clock = FakeTime()
    buf = BatchBuffer(max_size=2, max_age=1.0, clock=clock)
    buf.add(1)
    buf.add(2)
    assert buf.drain() == [1, 2]
    assert len(buf) == 0 and not buf.ready()
    clock.t = 50
    buf.add(3)  # tuổi tính lại từ phần tử đầu tiên của lô mới
    assert not buf.ready()


def test_invalid_size():
    with pytest.raises(ValueError):
        BatchBuffer(max_size=0, max_age=1.0)
