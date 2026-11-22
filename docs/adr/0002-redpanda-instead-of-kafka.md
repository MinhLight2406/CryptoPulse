# ADR-0002: Dùng Redpanda thay cho Apache Kafka

- Trạng thái: Chấp nhận
- Ngày: 2026-11-22

## Bối cảnh
Cần một message bus chạy trên máy cá nhân (Windows + Docker Desktop), tốn ít tài nguyên,
và dùng API Kafka để mọi thư viện client thông dụng chạy được.

## Phương án đã cân nhắc
1. Apache Kafka (KRaft): chuẩn công nghiệp, nhưng nặng hơn khi chạy local.
2. Redpanda: tương thích API Kafka, một tiến trình, nhẹ hơn, có sẵn công cụ `rpk` và Console.
3. Redis Streams: đơn giản, nhưng không phản ánh kỹ năng Kafka mà nhà tuyển dụng quan tâm.

## Quyết định
Chọn Redpanda cho môi trường phát triển. Code chỉ dùng API Kafka nên có thể đổi sang
Kafka thật mà không sửa logic.

## Hệ quả
- Giữ code ở mức API Kafka, không dùng tính năng riêng của Redpanda.
- Nếu cần so sánh, đo thêm trên Kafka và ghi vào `docs/benchmarks/`.
