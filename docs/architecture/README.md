# CryptoPulse Architecture

CryptoPulse provides an end-to-end simulated crypto market with a complete ML lifecycle.

## High-Level Architecture Flow

```
[ Historical Data / Scripts ]
            │
            ▼
    [ Replayer Service ]  ◄── [ Virtual Clock ]
            │
            ▼ (Topic: market.ticks)
  [ Feature Service ]
            │
            ▼ (Topic: features.streaming)
   [ Inference Service ] (Champion / Challenger)
      │               │
      ▼               ▼ (Topic: inference.predictions)
[ Evaluator Service ] [ Drift Monitor Service ]
      │                         │
      ▼                         ▼
[ Metrics / Postgres ]   [ Retrain Trigger / Alerts ]
```

## Services Overview
- **Replayer:** Emits ticks according to the Virtual Clock.
- **Feature Service:** Derives real-time streaming indicators.
- **Inference:** Produces predictions for live pairs using active models.
- **Evaluator:** Evaluates accuracy against delayed ground truth.
- **Drift Monitor:** Tracks statistical shifts in features and predictions.
- **API:** Web/API gateway for user interaction and monitoring.
