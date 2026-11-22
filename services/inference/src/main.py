"""Điểm vào của dịch vụ inference (chưa cài đặt)."""

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("inference")


def main() -> None:
    log.info("inference khởi động (skeleton)")


if __name__ == "__main__":
    main()
