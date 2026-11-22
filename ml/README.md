# ml

- `features/`   code tính đặc trưng, dùng chung cho train và serve
- `training/`   huấn luyện, walk-forward validation, log MLflow
- `evaluation/` so với baseline, calibration, AUC
- `drift/`      PSI / KS-test
- `notebooks/`  khám phá dữ liệu

Quy tắc: không dùng dữ liệu sau thời điểm dự đoán; không chia train/test ngẫu nhiên.
