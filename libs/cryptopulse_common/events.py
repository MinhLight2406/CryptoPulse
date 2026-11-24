"""Schema sự kiện dùng chung giữa các dịch vụ.

Quy tắc quan trọng: một nến chỉ "được biết" khi nó đã đóng, tức là tại
`available_at = open_time + interval_ms`. Mọi dịch vụ phải dùng mốc này làm giờ của sự kiện
để không nhìn thấy dữ liệu tương lai.
"""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

SCHEMA_VERSION = 1

# Thứ tự cột khi ghi vào ClickHouse (bảng candles); phải khớp CandleEvent.as_row().
CANDLE_COLUMNS = [
    "symbol",
    "interval_ms",
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trades",
    "taker_buy_base",
    "taker_buy_quote",
    "schema_version",
]


@dataclass(frozen=True)
class CandleEvent:
    symbol: str
    interval_ms: int
    open_time: int  # mili giây, UTC
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    trades: int
    taker_buy_base: float
    taker_buy_quote: float
    schema_version: int = SCHEMA_VERSION

    @property
    def available_at(self) -> int:
        """Thời điểm (ms) nến đã đóng và mới được phép phát ra."""
        return self.open_time + self.interval_ms

    @classmethod
    def from_row(cls, row: dict, interval_ms: int) -> "CandleEvent":
        return cls(
            symbol=row["symbol"],
            interval_ms=interval_ms,
            open_time=int(row["open_time"]),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
            quote_volume=float(row["quote_volume"]),
            trades=int(row["trades"]),
            taker_buy_base=float(row["taker_buy_base"]),
            taker_buy_quote=float(row["taker_buy_quote"]),
        )

    def as_row(self) -> tuple:
        """Một dòng để ghi vào ClickHouse, theo đúng thứ tự CANDLE_COLUMNS."""
        return (
            self.symbol,
            self.interval_ms,
            datetime.fromtimestamp(self.open_time / 1000, UTC),
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            self.quote_volume,
            self.trades,
            self.taker_buy_base,
            self.taker_buy_quote,
            self.schema_version,
        )

    def to_json(self) -> bytes:
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True).encode("utf-8")

    @classmethod
    def from_json(cls, data: bytes) -> "CandleEvent":
        return cls(**json.loads(data.decode("utf-8")))
