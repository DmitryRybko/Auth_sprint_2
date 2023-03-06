"""Module to connect to elasticsearch."""

from typing import Optional

from elasticsearch7 import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch | None:
    """Return ElasticSearch object to work with FastAPI."""
    return es
