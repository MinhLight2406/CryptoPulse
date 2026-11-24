# ADR-0005: Sự kiện nến, quy tắc "phát khi nến đã đóng" và thiết kế replayer

- Trạng thái: Chấp nhận
- Ngày: 2026-11-23

## Bối cảnh
Hệ thống ML phải học và dự đoán mà không nhìn thấy dữ liệu tương lai. Replayer là nơi quyết định
dữ liệu nào "đã được biết" tại mỗi thời điểm ảo.

## Quyết định
1. Mỗi nến phát ra một sự kiện `CandleEvent` (JSON, có `schema_version`) vào topic `candles`.
2. Một nến chỉ được phát khi đã đóng: `available_at = open_time + interval_ms`. Mọi dịch vụ dùng
   mốc này làm giờ của sự kiện.
3. Gộp các coin theo thứ tự (`available_at`, `symbol`) nên mỗi lần chạy cho kết quả giống hệt nhau.
4. Khóa tin nhắn là tên coin; topic có 1 partition để giữ thứ tự thời gian giữa các coin.
5. Tốc độ phát chỉnh được (`--speed`), hoặc nhanh nhất (`--max-speed`) để đo throughput.
6. Đổi tên topic `trades` thành `candles` vì dữ liệu là nến, không phải từng giao dịch.

## Hệ quả
- Một partition giới hạn throughput; chấp nhận được với 5 đến 20 coin ở mức nến 1 phút.
- Khi cần mở rộng, tách theo coin và chấp nhận chỉ giữ thứ tự trong từng coin.
- Sự kiện JSON dễ đọc và gỡ lỗi; có thể chuyển sang Avro/Protobuf nếu cần.
