"""Tên topic Kafka/Redpanda dùng chung toàn hệ thống."""

TRADES = "trades"  # nến/giao dịch được replayer phát lại
FEATURES = "features"  # đặc trưng đã tính theo cửa sổ
PREDICTIONS = "predictions"  # dự đoán của champion (và shadow/canary)
LABELS = "labels"  # kết quả thật, do evaluator ghép sau khi nhãn đến
DRIFT_EVENTS = "drift-events"  # cảnh báo drift
MODEL_EVENTS = "model-events"  # sự kiện promote/rollback model

ALL = [TRADES, FEATURES, PREDICTIONS, LABELS, DRIFT_EVENTS, MODEL_EVENTS]
