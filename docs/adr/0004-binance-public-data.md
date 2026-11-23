# ADR-0004: Dùng Binance Public Data (nến 1 phút) làm nguồn dữ liệu lịch sử

- Trạng thái: Chấp nhận
- Ngày: 2026-11-23

## Bối cảnh
Cần dữ liệu thị trường crypto lịch sử, miễn phí, tải được một lần để replay (xem ADR-0001).

## Phương án đã cân nhắc
1. Binance Public Data (data.binance.vision): file zip theo tháng, có CHECKSUM, không cần API key.
2. API REST của sàn: giới hạn tần suất, phải phân trang, khó lặp lại.
3. Dữ liệu từng giao dịch (trades): quá lớn so với nhu cầu dự đoán 15 phút và 1 giờ.

## Quyết định
Chọn phương án 1 với nến 1 phút. Kiểm tra CHECKSUM, chuẩn hóa mốc thời gian về mili giây
(dữ liệu từ 2025-01-01 dùng micro giây), kiểm tra nến trùng/thiếu/giá lỗi, lưu Parquet
theo `klines_1m/symbol=<SYM>/<YYYY-MM>.parquet`.

## Hệ quả
- Chỉ dùng cho học tập cá nhân; không commit và không phân phối lại dữ liệu.
- Phải tuân thủ điều khoản sử dụng của Binance.
- Nến 1 phút đủ cho mục tiêu; có thể gộp lên 5 phút, 15 phút, 1 giờ.
