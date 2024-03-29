"""Create log_history partitions module."""

import datetime

from logging import getLogger

from psycopg2 import connect

from flask_auth.project.settings import app_settings


logger = getLogger(__name__)


def create_log_history_partitions(
    year: str = datetime.datetime.now().strftime("%Y")
) -> None:
    """Create partitions for log_history table."""
    log_history_table_name: str = "log_history"
    with connect(
        dbname=app_settings.postgres_db,
        user=app_settings.postgres_user,
        password=app_settings.postgres_password,
        host=app_settings.postgres_host,
        port=app_settings.postgres_port
    ) as conn, conn.cursor() as cursor:
        for i in range(1, 12):
            cursor.execute(
                (
                    "CREATE TABLE IF NOT EXISTS "
                    f'"{log_history_table_name}_y{year}m{i}" '
                    f"PARTITION OF {log_history_table_name} "
                    f"FOR VALUES FROM ('{year}-{i}-01') "
                    f"TO ('{year}-{i+1}-01');"
                )
            )
            logger.info(
                f"Postgres partition {log_history_table_name}_y{year}m{i}"
            )

        cursor.execute(
            (
                "CREATE TABLE IF NOT EXISTS "
                f'"{log_history_table_name}_y{year}m12" '
                f"PARTITION OF {log_history_table_name} "
                f"FOR VALUES FROM ('{year}-12-01') "
                f"TO ('{year}-12-31');"
            )
        )
        logger.info(f"Postgres partition {log_history_table_name}_y{year}m12")


if __name__ == "__main__":
    create_log_history_partitions()
