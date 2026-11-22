# Feature Service

Computes real-time streaming market features over tick events consumed from the message broker.

## Computed Features
- Rolling Volume-Weighted Average Price (VWAP)
- Realized Volatility (5s, 30s, 60s windows)
- Order Book Imbalance (bid/ask volume ratio)
- Relative Strength Index (RSI) & Momentum indicators

## Running Locally

```bash
python src/main.py
```
