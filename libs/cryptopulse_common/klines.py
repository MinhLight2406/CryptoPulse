"""Đọc và kiểm tra chất lượng dữ liệu nến (klines) của Binance."""

import csv
import io
import zipfile
from dataclasses import dataclass

# Từ 2025-01-01, dữ liệu spot dùng micro giây; trước đó dùng mili giây.
_MICROSECOND_THRESHOLD = 10**14


def to_millis(ts: int) -> int:
    """Chuẩn hóa mốc thời gian về mili giây."""
    return ts // 1000 if ts >= _MICROSECOND_THRESHOLD else ts


def read_zip_text(zip_bytes: bytes) -> str:
    """Giải nén file CSV đầu tiên trong zip và trả về nội dung dạng chuỗi."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        name = zf.namelist()[0]
        return zf.read(name).decode("utf-8")


def parse_csv(text: str) -> list[dict]:
    """Chuyển nội dung CSV thành danh sách dòng; bỏ qua dòng tiêu đề nếu có."""
    rows: list[dict] = []
    for rec in csv.reader(io.StringIO(text)):
        if len(rec) < 11 or not rec[0].strip().isdigit():
            continue
        rows.append(
            {
                "open_time": to_millis(int(rec[0])),
                "open": float(rec[1]),
                "high": float(rec[2]),
                "low": float(rec[3]),
                "close": float(rec[4]),
                "volume": float(rec[5]),
                "close_time": to_millis(int(rec[6])),
                "quote_volume": float(rec[7]),
                "trades": int(rec[8]),
                "taker_buy_base": float(rec[9]),
                "taker_buy_quote": float(rec[10]),
            }
        )
    return rows


@dataclass
class QualityReport:
    rows: int
    duplicates: int
    out_of_order: int
    missing_candles: int
    bad_prices: int

    @property
    def ok(self) -> bool:
        return self.duplicates == 0 and self.bad_prices == 0 and self.out_of_order == 0


def check_quality(rows: list[dict], interval_ms: int = 60_000) -> QualityReport:
    """Đếm nến trùng, sai thứ tự, thiếu nến và giá bất thường."""
    times = [r["open_time"] for r in rows]
    unique = sorted(set(times))
    duplicates = len(times) - len(unique)
    out_of_order = sum(1 for a, b in zip(times, times[1:], strict=False) if b < a)

    missing = 0
    for a, b in zip(unique, unique[1:], strict=False):
        gap = (b - a) // interval_ms - 1
        if gap > 0:
            missing += gap

    bad = 0
    for r in rows:
        prices = (r["open"], r["high"], r["low"], r["close"])
        if min(prices) <= 0 or r["high"] < r["low"]:
            bad += 1
        elif not (r["low"] <= r["open"] <= r["high"] and r["low"] <= r["close"] <= r["high"]):
            bad += 1

    return QualityReport(
        rows=len(rows),
        duplicates=duplicates,
        out_of_order=out_of_order,
        missing_candles=missing,
        bad_prices=bad,
    )
