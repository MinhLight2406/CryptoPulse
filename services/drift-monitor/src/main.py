"""Điểm vào của dịch vụ drift-monitor (chưa cài đặt)."""

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("drift-monitor")


def main() -> None:
    log.info("drift-monitor khởi động (skeleton)")


if __name__ == "__main__":
    main()
