# API Gateway Service

HTTP and WebSocket API gateway exposing live market simulation controls, real-time predictions, drift status, and model metrics.

## Endpoints
- `GET /health`: Service health check.
- `GET /sim/clock`: Current virtual clock status, speed, and timestamp.
- `POST /sim/clock/speed`: Adjust simulation speed.
- `GET /predictions/latest`: Latest model predictions.
- `GET /metrics`: Prometheus metrics scrape target.

## Running Locally

```bash
python src/main.py
```
