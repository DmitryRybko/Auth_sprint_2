"""DB Getter module."""

from typing import Any, Optional

from elasticsearch7 import AsyncElasticsearch
from fastapi import Depends

from db.base_db import BaseDB
from db.elastic_db import ElasticDB

from db.elastic import get_elastic

es: Optional[BaseDB] = None


async def get_db(
    elastic: AsyncElasticsearch = Depends(get_elastic)
) -> Any | None:
    """Return ElasticSearch object to work with FastAPI.

    Args:
        elastic (AsyncElasticsearch): item of ElasticSearch service.
    Returns:
        ElasticDB as DB item.
    """
    return ElasticDB(elastic)
