import os

import sentry_sdk


def connect_sentry():
    """Connect Sentry monitoring server."""
    sentry_dsn: str = os.environ.get("SENTRY_DSN", "")

    if sentry_dsn:
        sentry_sdk.init(
            dsn = sentry_dsn,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=1.0,
        )