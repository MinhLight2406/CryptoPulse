"""Điểm vào của dịch vụ feature-service (chưa cài đặt)."""

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("feature-service")


def main() -> None:
    log.info("feature-service khởi động (skeleton)")


if __name__ == "__main__":
    main()
