# Evaluator Service

Matches delayed ground-truth market prices with earlier model predictions to evaluate accuracy in real time.

## Metrics Computed
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Directional Accuracy (% of correct price movement predictions)
- Profit & Loss (PnL) simulation under basic execution assumptions

## Running Locally

```bash
python src/main.py
```
