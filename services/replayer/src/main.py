"""Replayer: phát lại nến lịch sử vào Redpanda theo đồng hồ ảo.

Ví dụ:
    python services/replayer/src/main.py --dry-run --max-speed --limit 10
    python services/replayer/src/main.py --speed 1440
"""

import argparse
import itertools
import logging
import os
import sys
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libs"))
from cryptopulse_common import VirtualClock, topics  # noqa: E402
from cryptopulse_common.events import CandleEvent  # noqa: E402
from cryptopulse_common.replay import merge_by_time, paced  # noqa: E402

log = logging.getLogger("replayer")
INTERVALS = {"1m": 60_000, "5m": 300_000}


def parse_ts(text: str) -> int:
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return int(dt.timestamp() * 1000)


def load_symbol(root: Path, symbol: str, interval: str) -> Iterator[CandleEvent]:
    interval_ms = INTERVALS[interval]
    folder = root / f"klines_{interval}" / f"symbol={symbol}"
    for path in sorted(folder.glob("*.parquet")):
        for row in pq.read_table(path).to_pylist():
            yield CandleEvent.from_row(row, interval_ms)


def within(stream: Iterator[CandleEvent], start: int | None, end: int | None):
    for ev in stream:
        if start is not None and ev.available_at < start:
            continue
        if end is not None and ev.available_at >= end:
            return
        yield ev


def build_producer():
    from confluent_kafka import Producer

    return Producer(
        {
            "bootstrap.servers": os.environ.get("KAFKA_BROKERS", "localhost:19092"),
            "acks": "all",
            "enable.idempotence": True,
            "linger.ms": 5,
        }
    )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/parquet")
    ap.add_argument("--symbols", nargs="+", help="mặc định: mọi symbol có trong thư mục data")
    ap.add_argument("--interval", default="1m", choices=INTERVALS)
    ap.add_argument("--start", help="ISO, ví dụ 2025-01-01 hoặc 2025-01-01T08:00")
    ap.add_argument("--end", help="ISO, không bao gồm mốc này")
    ap.add_argument("--speed", type=float, default=1440.0, help="1440 = 1 ngày ảo trong 1 phút")
    ap.add_argument("--max-speed", action="store_true", help="không điều tiết, phát nhanh nhất")
    ap.add_argument("--limit", type=int, help="chỉ phát N sự kiện đầu tiên")
    ap.add_argument("--dry-run", action="store_true", help="in ra thay vì gửi vào Redpanda")
    args = ap.parse_args()

    root = Path(args.data)
    base = root / f"klines_{args.interval}"
    symbols = args.symbols or sorted(p.name.split("=", 1)[1] for p in base.glob("symbol=*"))
    if not symbols:
        log.error("Khong tim thay du lieu trong %s. Hay chay download_klines.py truoc.", base)
        return 2

    start = parse_ts(args.start) if args.start else None
    end = parse_ts(args.end) if args.end else None
    streams = [within(load_symbol(root, s, args.interval), start, end) for s in symbols]

    it = merge_by_time(streams)
    first = next(it, None)
    if first is None:
        log.error("Khong co su kien nao trong khoang thoi gian da chon.")
        return 2
    stream = itertools.chain([first], it)
    if args.limit:
        stream = itertools.islice(stream, args.limit)
    if not args.max_speed:
        clock = VirtualClock(datetime.fromtimestamp(first.available_at / 1000, UTC), args.speed)
        stream = paced(stream, clock)

    producer = None if args.dry_run else build_producer()
    errors = 0

    def on_delivery(err, _msg):
        nonlocal errors
        if err is not None:
            errors += 1
            log.error("Gui that bai: %s", err)

    count = 0
    t0 = time.monotonic()
    last = first
    for ev in stream:
        last = ev
        count += 1
        if producer is None:
            if count <= 20:
                at = datetime.fromtimestamp(ev.available_at / 1000, UTC)
                print(f"{at:%Y-%m-%d %H:%M} {ev.symbol} close={ev.close}")
        else:
            while True:
                try:
                    producer.produce(
                        topics.CANDLES,
                        key=ev.symbol.encode(),
                        value=ev.to_json(),
                        on_delivery=on_delivery,
                    )
                    break
                except BufferError:
                    producer.poll(0.5)
            producer.poll(0)
        if count % 10_000 == 0:
            at = datetime.fromtimestamp(ev.available_at / 1000, UTC)
            log.info("da phat %d su kien, gio ao %s", count, f"{at:%Y-%m-%d %H:%M}")

    if producer is not None:
        producer.flush(30)
    elapsed = max(time.monotonic() - t0, 1e-9)
    end_at = datetime.fromtimestamp(last.available_at / 1000, UTC)
    log.info(
        "Xong: %d su kien, %.1f giay, %.0f su kien/giay, gio ao cuoi %s, loi gui=%d",
        count,
        elapsed,
        count / elapsed,
        f"{end_at:%Y-%m-%d %H:%M}",
        errors,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
