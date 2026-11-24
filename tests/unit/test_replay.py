from datetime import UTC, datetime

import pytest
from cryptopulse_common import VirtualClock
from cryptopulse_common.events import CandleEvent
from cryptopulse_common.replay import merge_by_time, paced

MIN = 60_000
T0 = 1_733_011_200_000  # 2024-12-01 00:00 UTC


def candle(symbol: str, minute: int, close: float = 100.0) -> CandleEvent:
    return CandleEvent(
        symbol=symbol,
        interval_ms=MIN,
        open_time=T0 + minute * MIN,
        open=close,
        high=close + 1,
        low=close - 1,
        close=close,
        volume=1.0,
        quote_volume=100.0,
        trades=3,
        taker_buy_base=0.5,
        taker_buy_quote=50.0,
    )


def test_available_at_is_close_time():
    assert candle("BTCUSDT", 0).available_at == T0 + MIN


def test_json_roundtrip():
    ev = candle("ETHUSDT", 7, close=3500.5)
    assert CandleEvent.from_json(ev.to_json()) == ev


def test_from_row_converts_types():
    row = {
        "symbol": "BTCUSDT",
        "open_time": T0,
        "open": "1",
        "high": "2",
        "low": "0.5",
        "close": "1.5",
        "volume": "3",
        "quote_volume": "4",
        "trades": "5",
        "taker_buy_base": "6",
        "taker_buy_quote": "7",
    }
    ev = CandleEvent.from_row(row, MIN)
    assert ev.trades == 5 and ev.high == 2.0 and ev.interval_ms == MIN


def test_merge_orders_by_time_then_symbol():
    btc = [candle("BTCUSDT", i) for i in range(3)]
    eth = [candle("ETHUSDT", i) for i in range(3)]
    merged = list(merge_by_time([eth, btc]))
    assert [(e.available_at, e.symbol) for e in merged] == [
        (T0 + MIN, "BTCUSDT"),
        (T0 + MIN, "ETHUSDT"),
        (T0 + 2 * MIN, "BTCUSDT"),
        (T0 + 2 * MIN, "ETHUSDT"),
        (T0 + 3 * MIN, "BTCUSDT"),
        (T0 + 3 * MIN, "ETHUSDT"),
    ]


def test_merge_is_deterministic():
    def run():
        return [
            (e.symbol, e.open_time)
            for e in merge_by_time(
                [[candle("B", i) for i in range(5)], [candle("A", i) for i in range(5)]]
            )
        ]

    assert run() == run()


class FakeTime:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += seconds


def test_paced_waits_for_virtual_time():
    fake = FakeTime()
    first_due = datetime.fromtimestamp((T0 + MIN) / 1000, UTC)
    clock = VirtualClock(first_due, speed=60, real_time=fake)
    events = [candle("BTCUSDT", i) for i in range(3)]  # cách nhau 60 giây ảo
    out = list(paced(events, clock, sleep=fake.sleep))
    assert out == events
    # 2 khoảng cách x 60 giây ảo / tốc độ 60 = 2 giây thật
    assert fake.t - 100.0 == pytest.approx(2.0, abs=0.01)
