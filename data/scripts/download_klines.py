"""Tải nến 1 phút (klines) từ Binance Public Data, kiểm tra, rồi lưu thành Parquet.

Ví dụ:
    python data/scripts/download_klines.py --symbols BTCUSDT ETHUSDT --start 2024-12 --end 2025-02

Dữ liệu chỉ dùng cho học tập cá nhân. KHÔNG commit và KHÔNG phân phối lại file dữ liệu.
"""

import argparse
import hashlib
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs"))
from cryptopulse_common import klines  # noqa: E402

BASE = "https://data.binance.vision/data/spot/monthly/klines"
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "UNIUSDT"]


def month_range(start: str, end: str) -> list[str]:
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    out = []
    y, m = sy, sm
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def fetch(url: str, retries: int = 3) -> bytes:
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise
            if attempt == retries:
                raise
        except urllib.error.URLError:
            if attempt == retries:
                raise
        time.sleep(2 * attempt)
    raise RuntimeError("unreachable")


def verify_checksum(zip_bytes: bytes, checksum_text: str) -> bool:
    expected = checksum_text.split()[0].strip().lower()
    return hashlib.sha256(zip_bytes).hexdigest() == expected


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", nargs="+", default=DEFAULT_SYMBOLS)
    ap.add_argument("--start", default="2024-12", help="YYYY-MM")
    ap.add_argument("--end", default="2025-02", help="YYYY-MM")
    ap.add_argument("--interval", default="1m")
    ap.add_argument("--out", default="data/parquet")
    ap.add_argument("--pause", type=float, default=1.0, help="giây nghỉ giữa các lần tải")
    args = ap.parse_args()

    interval_ms = {"1m": 60_000, "5m": 300_000}.get(args.interval)
    if interval_ms is None:
        print("Chi ho tro interval 1m hoac 5m")
        return 2

    problems = 0
    for symbol in args.symbols:
        for month in month_range(args.start, args.end):
            name = f"{symbol}-{args.interval}-{month}"
            url = f"{BASE}/{symbol}/{args.interval}/{name}.zip"
            target = Path(args.out) / f"klines_{args.interval}" / f"symbol={symbol}" / f"{month}.parquet"
            if target.exists():
                print(f"SKIP  {name} (da co)")
                continue
            try:
                zip_bytes = fetch(url)
                checksum = fetch(url + ".CHECKSUM").decode("utf-8")
            except urllib.error.HTTPError as exc:
                print(f"FAIL  {name}: HTTP {exc.code}")
                problems += 1
                continue
            if not verify_checksum(zip_bytes, checksum):
                print(f"FAIL  {name}: sai checksum")
                problems += 1
                continue

            rows = klines.parse_csv(klines.read_zip_text(zip_bytes))
            report = klines.check_quality(rows, interval_ms)
            for r in rows:
                r["symbol"] = symbol
            target.parent.mkdir(parents=True, exist_ok=True)
            pq.write_table(pa.Table.from_pylist(rows), target, compression="zstd")
            flag = "OK  " if report.ok else "WARN"
            print(
                f"{flag}  {name}: {report.rows} nen, trung={report.duplicates}, "
                f"thieu={report.missing_candles}, gia_loi={report.bad_prices}"
            )
            time.sleep(args.pause)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
