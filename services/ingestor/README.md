# ingestor

**Vai trò:** Ghi nến từ Redpanda vào ClickHouse, tự khử trùng lặp

| | |
|---|---|
| Đầu vào | Topic candles |
| Đầu ra | Bảng candles trong ClickHouse |

Bảng dùng `ReplacingMergeTree` với khóa `(symbol, interval_ms, open_time)`: nếu cùng một nến
được ghi nhiều lần (replay nhiều lần) thì khi truy vấn với `FINAL` chỉ còn một bản.

Consumer chỉ commit offset sau khi ghi ClickHouse thành công (ít nhất một lần), kết hợp với
khử trùng lặp nên kết quả cuối cùng không bị nhân đôi.

## Trạng thái
- [x] Skeleton
- [x] Logic chính
- [x] Test
- [ ] Dockerfile chạy được trong CI
