"""Ingestor: đọc topic candles và ghi vào ClickHouse theo lô.

Ví dụ:
    python services/ingestor/src/main.py --idle-exit 10     # ghi hết rồi thoát
    python services/ingestor/src/main.py                    # chạy liên tục
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libs"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cryptopulse_common import topics  # noqa: E402
from cryptopulse_common.batching import BatchBuffer  # noqa: E402
from cryptopulse_common.events import CANDLE_COLUMNS, SCHEMA_VERSION, CandleEvent  # noqa: E402
from schema import CREATE_TABLE  # noqa: E402

log = logging.getLogger("ingestor")


def env(name: str, default: str) -> str:
    return os.environ.get(name, default)


def make_client():
    import clickhouse_connect

    db = env("CLICKHOUSE_DB", "cryptopulse")
    client = clickhouse_connect.get_client(
        host=env("CLICKHOUSE_HOST", "localhost"),
        port=int(env("CLICKHOUSE_PORT", "8123")),
        username=env("CLICKHOUSE_USER", "cryptopulse"),
        password=env("CLICKHOUSE_PASSWORD", "change_me"),
    )
    client.command(f"CREATE DATABASE IF NOT EXISTS {db}")
    client.command(CREATE_TABLE.format(db=db))
    return client, db


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default="ingestor", help="consumer group id")
    ap.add_argument("--batch", type=int, default=5000, help="số sự kiện tối đa mỗi lô")
    ap.add_argument("--max-age", type=float, default=1.0, help="giây tối đa trước khi xả lô")
    ap.add_argument(
        "--idle-exit",
        type=float,
        default=0.0,
        help="thoát khi không có tin nhắn mới sau N giây (0 = chạy mãi)",
    )
    args = ap.parse_args()

    from confluent_kafka import Consumer

    client, db = make_client()
    consumer = Consumer(
        {
            "bootstrap.servers": env("KAFKA_BROKERS", "localhost:19092"),
            "group.id": args.group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topics.CANDLES])

    buf: BatchBuffer[CandleEvent] = BatchBuffer(args.batch, args.max_age)
    inserted = 0
    skipped = 0

    def flush() -> None:
        nonlocal inserted
        items = buf.drain()
        if not items:
            return
        client.insert(
            "candles",
            [e.as_row() for e in items],
            column_names=CANDLE_COLUMNS,
            database=db,
        )
        consumer.commit(asynchronous=False)  # chỉ commit sau khi ghi thành công
        inserted += len(items)
        log.info("da ghi %d nen (tong %d)", len(items), inserted)

    last_activity = time.monotonic()
    t0 = last_activity
    try:
        while True:
            msg = consumer.poll(0.5)
            if msg is None:
                if buf.ready():
                    flush()
                if args.idle_exit and time.monotonic() - last_activity >= args.idle_exit:
                    log.info("khong con tin nhan moi sau %.0f giay, thoat", args.idle_exit)
                    break
                continue
            if msg.error():
                log.error("loi consumer: %s", msg.error())
                continue
            last_activity = time.monotonic()
            try:
                ev = CandleEvent.from_json(msg.value())
            except (ValueError, TypeError, KeyError) as exc:
                skipped += 1
                log.warning("bo qua tin nhan loi dinh dang (offset %s): %s", msg.offset(), exc)
                continue
            if ev.schema_version != SCHEMA_VERSION:
                log.warning("schema_version %s khac %s", ev.schema_version, SCHEMA_VERSION)
            buf.add(ev)
            if buf.ready():
                flush()
    except KeyboardInterrupt:
        log.info("nhan Ctrl+C, xa lo cuoi")
    finally:
        flush()
        consumer.close()

    elapsed = max(time.monotonic() - t0, 1e-9)
    log.info("Xong: ghi %d nen, bo qua %d, %.1f giay", inserted, skipped, elapsed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
