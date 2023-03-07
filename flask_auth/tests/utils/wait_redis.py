#!/usr/bin/env python3
"""Redis waiter script."""

import os
import time
from logging import getLogger

import redis  # type: ignore


logger = getLogger(__name__)


def main() -> None:
    """Return None when Redis service is available."""
    redis_host: str = os.environ.get("REDIS_HOST", "localhost")
    redis_port: str = os.environ.get("REDIS_PORT", "6379")
    logger.debug(f'Wait redis on {redis_host}:{redis_port}')
    timeout_sec: int = 2 * 60
    while timeout_sec > 0:
        try:
            r = redis.from_url(
                f"redis://{redis_host}:{redis_port}",
                encoding="utf8",
                decode_responses=True
            )
            if r.ping():
                logger.info(f'Redis is available on {redis_host}:{redis_port}')
                return
        except Exception:
            pass
        time.sleep(1)
        timeout_sec -= 1
    raise Exception("Waiting Redis timeout")


if __name__ == "__main__":
    main()
