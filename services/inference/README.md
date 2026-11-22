# Inference Service

Real-time model prediction engine supporting Champion/Challenger canary deployments and model A/B testing.

## Capabilities
- Low-latency inference scoring incoming streaming features.
- Canary traffic splitting between production champion model and candidate challenger models.
- Emits predictions to `cryptopulse.inference.predictions.v1`.

## Running Locally

```bash
python src/main.py
```
