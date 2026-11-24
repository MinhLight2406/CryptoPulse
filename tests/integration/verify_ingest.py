"""Kiểm tra dữ liệu trong ClickHouse khớp với file Parquet gốc.

Ví dụ:
    python tests/integration/verify_ingest.py --start 2024-12-01 --end 2024-12-02

So sánh theo từng coin: số nến, tổng close, tổng volume, tổng trades. Truy vấn dùng FINAL để
khử trùng lặp, nên replay nhiều lần vẫn phải cho cùng một kết quả.
"""

import argparse
import math
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq

INTERVALS = {"1m": 60_000, "5m": 300_000}


def parse_ts(text: str) -> int:
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return int(dt.timestamp() * 1000)


def expected_from_parquet(root: Path, interval: str, start_ms: int, end_ms: int) -> dict:
    """Tổng hợp từ file gốc, theo đúng quy tắc của replayer: lấy nến có available_at trong
    [start, end), với available_at = open_time + interval."""
    interval_ms = INTERVALS[interval]
    result: dict[str, dict] = {}
    for folder in sorted((root / f"klines_{interval}").glob("symbol=*")):
        symbol = folder.name.split("=", 1)[1]
        agg = {"n": 0, "close": 0.0, "volume": 0.0, "trades": 0}
        for path in sorted(folder.glob("*.parquet")):
            cols = pq.read_table(path, columns=["open_time", "close", "volume", "trades"])
            data = cols.to_pydict()
            for ot, close, vol, trades in zip(
                data["open_time"], data["close"], data["volume"], data["trades"], strict=True
            ):
                if start_ms <= ot + interval_ms < end_ms:
                    agg["n"] += 1
                    agg["close"] += close
                    agg["volume"] += vol
                    agg["trades"] += trades
        if agg["n"]:
            result[symbol] = agg
    return result


def build_query(table: str, interval_ms: int, lo_ms: int, hi_ms: int, final: bool) -> str:
    mode = "FINAL" if final else ""
    return f"""
SELECT symbol, count() AS n, sum(close) AS close, sum(volume) AS volume, sum(trades) AS trades
FROM {table} {mode}
WHERE interval_ms = {interval_ms}
  AND open_time >= fromUnixTimestamp64Milli({lo_ms}, 'UTC')
  AND open_time <  fromUnixTimestamp64Milli({hi_ms}, 'UTC')
GROUP BY symbol
ORDER BY symbol
"""


def compare(expected: dict, actual: dict) -> list[str]:
    problems = []
    for symbol in sorted(set(expected) | set(actual)):
        e, a = expected.get(symbol), actual.get(symbol)
        if e is None or a is None:
            problems.append(f"{symbol}: thieu o {'ClickHouse' if a is None else 'Parquet'}")
            continue
        if e["n"] != a["n"]:
            problems.append(f"{symbol}: so nen {a['n']} != {e['n']}")
        for key in ("close", "volume"):
            if not math.isclose(e[key], a[key], rel_tol=1e-9):
                problems.append(f"{symbol}: tong {key} {a[key]} != {e[key]}")
        if e["trades"] != a["trades"]:
            problems.append(f"{symbol}: tong trades {a['trades']} != {e['trades']}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/parquet")
    ap.add_argument("--interval", default="1m", choices=INTERVALS)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    args = ap.parse_args()

    import clickhouse_connect

    interval_ms = INTERVALS[args.interval]
    start_ms, end_ms = parse_ts(args.start), parse_ts(args.end)
    lo, hi = start_ms - interval_ms, end_ms - interval_ms  # đổi từ available_at sang open_time
    db = os.environ.get("CLICKHOUSE_DB", "cryptopulse")
    client = clickhouse_connect.get_client(
        host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
        port=int(os.environ.get("CLICKHOUSE_PORT", "8123")),
        username=os.environ.get("CLICKHOUSE_USER", "cryptopulse"),
        password=os.environ.get("CLICKHOUSE_PASSWORD", "change_me"),
    )
    table = f"{db}.candles"

    def fetch(final: bool) -> dict:
        rows = client.query(build_query(table, interval_ms, lo, hi, final)).result_rows
        return {r[0]: {"n": r[1], "close": r[2], "volume": r[3], "trades": r[4]} for r in rows}

    expected = expected_from_parquet(Path(args.data), args.interval, start_ms, end_ms)
    final = fetch(final=True)
    raw = fetch(final=False)

    print(f"{'coin':10} {'parquet':>9} {'FINAL':>9} {'khong FINAL':>12}")
    for symbol in sorted(set(expected) | set(final)):
        print(
            f"{symbol:10} {expected.get(symbol, {}).get('n', 0):>9} "
            f"{final.get(symbol, {}).get('n', 0):>9} {raw.get(symbol, {}).get('n', 0):>12}"
        )
    problems = compare(expected, final)
    total_expected = sum(v["n"] for v in expected.values())
    total_raw = sum(v["n"] for v in raw.values())
    print(
        f"\nTong: parquet={total_expected}, FINAL={sum(v['n'] for v in final.values())}, "
        f"khong FINAL={total_raw}"
    )
    if problems:
        print("\nKHONG KHOP:")
        for p in problems:
            print(" -", p)
        return 1
    if not expected:
        print("Khong co du lieu trong khoang thoi gian da chon.")
        return 2
    print("\nPASS: ClickHouse (FINAL) khop voi file Parquet goc.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
