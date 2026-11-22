# ADR-0001: Chạy mô phỏng bằng dữ liệu lịch sử và đồng hồ ảo

- Trạng thái: Chấp nhận
- Ngày: 2026-11-22

## Bối cảnh
Dự án là sản phẩm rèn luyện ML + DevOps, mỗi ngày chỉ dành khoảng 1 giờ. Cần kết quả lặp lại
được, không phụ thuộc mạng hay API của sàn, và phải thấy được model "sống" qua nhiều ngày
thị trường trong vài phút.

## Phương án đã cân nhắc
1. Kết nối live tới sàn: dữ liệu thật nhưng không lặp lại, phụ thuộc điều khoản/API, khó đưa vào CI.
2. Phát lại dữ liệu lịch sử với đồng hồ ảo: lặp lại được, tua nhanh được, chủ động tạo drift
   bằng cách chọn giai đoạn đổi chế độ.

## Quyết định
Chọn phương án 2. Mọi dịch vụ đọc thời gian từ `VirtualClock`
(`libs/cryptopulse_common/clock.py`), không gọi `datetime.now()` trực tiếp.

## Hệ quả
- Phải kỷ luật: cấm dùng giờ máy trong logic nghiệp vụ.
- Chia dữ liệu theo thời gian (walk-forward) để tránh rò rỉ tương lai.
- Có thể thêm collector live sau như một adapter bổ sung.
