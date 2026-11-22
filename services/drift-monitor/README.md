# Drift Monitor Service

Tracks statistical data drift and concept drift across input feature distributions and prediction outputs.

## Tests & Methods
- Kolmogorov-Smirnov (KS) test for numerical continuous features
- Population Stability Index (PSI) with alert threshold (>0.2 = substantial drift)
- Jensen-Shannon Divergence
- Emits alerts to `cryptopulse.monitoring.drift.v1` and triggers retrain workflows

## Running Locally

```bash
python src/main.py
```
