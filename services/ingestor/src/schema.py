"""Định nghĩa bảng ClickHouse cho nến."""

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS {db}.candles
(
    symbol          LowCardinality(String),
    interval_ms     UInt32,
    open_time       DateTime64(3, 'UTC'),
    open            Float64,
    high            Float64,
    low             Float64,
    close           Float64,
    volume          Float64,
    quote_volume    Float64,
    trades          UInt32,
    taker_buy_base  Float64,
    taker_buy_quote Float64,
    schema_version  UInt8,
    ingested_at     DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(ingested_at)
PARTITION BY toYYYYMM(open_time)
ORDER BY (symbol, interval_ms, open_time)
"""
