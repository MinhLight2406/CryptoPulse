from datetime import UTC

from cryptopulse_common.events import CANDLE_COLUMNS, CandleEvent

T0 = 1_733_011_200_000  # 2024-12-01 00:00 UTC


def make_event(close: float = 123.5) -> CandleEvent:
    return CandleEvent(
        symbol="BTCUSDT",
        interval_ms=60_000,
        open_time=T0,
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


def test_as_row_matches_columns():
    row = make_event().as_row()
    assert len(row) == len(CANDLE_COLUMNS)
    assert row[CANDLE_COLUMNS.index("symbol")] == "BTCUSDT"
    assert row[CANDLE_COLUMNS.index("close")] == 123.5


def test_as_row_open_time_is_utc_datetime():
    open_time = make_event().as_row()[CANDLE_COLUMNS.index("open_time")]
    assert open_time.tzinfo is UTC
    assert int(open_time.timestamp() * 1000) == T0
