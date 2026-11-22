# Replayer Service

Replays historical cryptocurrency market data (trades, quotes, L2 orderbook ticks) at configurable speeds using the Virtual Clock.

## Features
- Read compressed Parquet tick files from `data/parquet/`.
- Emit events in chronological order to `cryptopulse.market.ticks.v1`.
- Configurable playback speed (1x real-time, 10x, 100x, or discrete tick intervals).

## Running Locally

```bash
python src/main.py
```
