"""Tên topic Kafka/Redpanda dùng chung toàn hệ thống."""

CANDLES = "candles"  # nến 1 phút do replayer phát lại, một sự kiện cho mỗi nến đã đóng
FEATURES = "features"  # đặc trưng đã tính theo cửa sổ
PREDICTIONS = "predictions"  # dự đoán của champion (và shadow/canary)
LABELS = "labels"  # kết quả thật, do evaluator ghép sau khi nhãn đến
DRIFT_EVENTS = "drift-events"  # cảnh báo drift
MODEL_EVENTS = "model-events"  # sự kiện promote/rollback model

ALL = [CANDLES, FEATURES, PREDICTIONS, LABELS, DRIFT_EVENTS, MODEL_EVENTS]
