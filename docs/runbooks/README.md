# CryptoPulse Operational Runbooks

## Runbook 1: Starting the Local Environment
1. Ensure Docker daemon is running.
2. Run infrastructure services:
   ```bash
   make compose-up
   ```
3. Verify Redpanda Console is accessible at `http://localhost:8080`.

## Runbook 2: Running the Replayer Simulation
1. Adjust simulation speed in `.env` (e.g. `SIMULATION_SPEED=5.0`).
2. Start the replayer:
   ```bash
   python services/replayer/src/main.py
   ```

## Runbook 3: Investigating Drift Alerts
1. Check `DRIFT_ALERTS` topic in Redpanda Console.
2. Review Grafana Drift Dashboard (`http://localhost:3000`).
3. If PSI > 0.25, inspect recent feature distributions in `ml/drift/` and trigger retrain pipeline.
