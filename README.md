# CryptoPulse

Mô phỏng thị trường crypto bằng dữ liệu lịch sử phát lại với **đồng hồ ảo**, trên đó chạy một
hệ thống ML hoàn chỉnh: dự đoán tăng/giảm theo từng coin và nhóm đầu tư, chấm điểm tự động,
phát hiện drift, retrain, champion/challenger, canary.

> **Chỉ là mô phỏng phục vụ học tập, không phải lời khuyên đầu tư.**

*A simulated crypto market with a full ML lifecycle: live prediction, auto-scoring, drift
detection, retrain, champion/challenger canary.*

## Chạy nhanh (Windows PowerShell)

Yêu cầu: Docker Desktop đang mở, Python 3.11+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

.\scripts\check.ps1          # lint + test + kiểm tra compose
.\scripts\up.ps1             # dựng hạ tầng
.\scripts\smoke.ps1          # kiểm tra các dịch vụ đã sống
.\scripts\create-topics.ps1  # tạo topic Redpanda
.\scripts\down.ps1           # tắt hạ tầng
```

| Dịch vụ | Địa chỉ |
|---|---|
| Redpanda Console | http://localhost:8080 |
| MLflow | http://localhost:5000 |
| ClickHouse HTTP | http://localhost:8123 |

## Cấu trúc

```text
services/       replayer, feature-service, inference, evaluator, drift-monitor, api
libs/           cryptopulse_common (đồng hồ ảo, tên topic)
apps/web/       giao diện
ml/             đặc trưng, huấn luyện, đánh giá, drift
orchestration/  Dagster (retrain)
data/           script tải dữ liệu, schema, dbt
infra/          compose, k8s, argocd, rollouts, terraform
observability/  Prometheus, Grafana, alert, SLO
tests/          unit, integration, e2e, load, chaos
docs/           adr, architecture, runbooks, postmortems, benchmarks
scripts/        script PowerShell chạy trên máy
```

## Lộ trình

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| 0 | Nền móng: khung dự án, hạ tầng local, kiểm tra | Đang làm |
| 1 | Dữ liệu + Replayer | Chưa |
| 2 | Feature + danh sách tăng/giảm | Chưa |
| 3 | ML v1 (baseline, walk-forward) | Chưa |
| 4 | ML live (inference, evaluator) | Chưa |
| 5 | Drift + retrain + shadow | Chưa |
| 6 | DevOps hoàn chỉnh (k3s, ArgoCD, canary) | Chưa |
| 7 | Chaos + hoàn thiện | Chưa |

## Số liệu (điền sau khi đo)

| Chỉ số | Giá trị |
|---|---|
| AUC / accuracy so với baseline | _chưa đo_ |
| Độ trễ inference p95 | _chưa đo_ |
| Thời gian CI trước/sau cache | _chưa đo_ |
| Thời gian từ drift đến model mới | _chưa đo_ |

## Giấy phép

MIT, xem file `LICENSE`.
