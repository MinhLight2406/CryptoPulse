# ADR-0003: Hoãn dùng MinIO, lưu Parquet trong thư mục cục bộ

- Trạng thái: Chấp nhận
- Ngày: 2026-11-23

## Bối cảnh
Image `minio/minio` không còn kéo được từ Docker Hub (pull access denied), và nguồn thay thế
chưa rõ ràng. Ở Giai đoạn 1 dự án chỉ cần lưu file Parquet lịch sử để replay.

## Phương án đã cân nhắc
1. Dùng quay.io hoặc bản phản chiếu của MinIO: các nguồn không thống nhất, phụ thuộc bên thứ ba.
2. Dùng bản fork hoặc kho S3 khác (ví dụ Garage, SeaweedFS): cần đánh giá thêm.
3. Lưu Parquet trong `data/parquet/` trên máy: đơn giản, đủ cho mô phỏng.

## Quyết định
Chọn phương án 3. Bỏ MinIO khỏi docker-compose. Khi thật sự cần kho kiểu S3
(ví dụ Giai đoạn 6 trên Kubernetes), đánh giá lại phương án 2 và ghi ADR mới.

## Hệ quả
- Hạ tầng gọn hơn: Redpanda, Console, Redis, ClickHouse, MLflow.
- Artifact của MLflow lưu trong volume Docker thay vì S3.
