#!/usr/bin/env python3
"""ElasticSearch waiter script."""

import os
import time

from elasticsearch7 import Elasticsearch


def main() -> None:
    """Return None when Elasticsearch service is available."""
    es_host: str = os.environ.get('ELASTIC_HOST', 'localhost')
    es_port: str = os.environ.get('ELASTIC_PORT', '9200')
    timeout_sec: int = 2 * 60
    while timeout_sec > 0:
        try:
            es = Elasticsearch(
                hosts=f'http://{es_host}:{es_port}',
                validate_cert=False,
                use_ssl=False
            )
            if es.ping():
                return
        except Exception:
            pass
        time.sleep(1)
        timeout_sec -= 1
    raise Exception('Waiting Elasticsearch timeout')


if __name__ == '__main__':
    main()
