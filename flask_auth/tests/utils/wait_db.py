#!/usr/bin/env python3
"""Script to wait when postgresql database is available."""

import os
from logging import getLogger
from time import sleep

from psycopg2 import connect


logger = getLogger(__name__)


def main() -> None:
    """Return if database is available."""
    db_name: str = os.environ.get("POSTGRES_DB", "_")
    db_user: str = os.environ.get("POSTGRES_USER", "app")
    db_password: str = os.environ.get("POSTGRES_PASSWORD", "123")
    db_host: str = os.environ.get("POSTGRES_HOST", "localhost")
    db_port: int = int(os.environ.get("POSTGRES_PORT", "5432"))
    logger.debug(f'Wait postgres on {db_host}:{db_port}')

    timeout_sec: int = 60
    while timeout_sec > 0:
        try:
            connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
        except Exception:
            sleep(1)
        else:
            logger.info(f"Postgres is available on {db_host}:{db_port}")
            return
        timeout_sec -= 1
    raise Exception(f"Timeout. There is no DB on {db_host}:{db_port}")


if __name__ == "__main__":
    main()
