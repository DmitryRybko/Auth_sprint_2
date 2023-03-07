"""Base model module."""

import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default) -> str:
    """Return JSON string.

    Needed because orjson returns bytes but pydantic requires unicode.
    """
    return orjson.dumps(v, default=default).decode()


class Base(BaseModel):
    """Base model to aggregate base fields and methods."""

    class Config:
        """Config class for BaseAPIModel.

        It changes default working with JSON to orjson.
        """

        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseAPIModel(Base):
    """BaseAPIModel to create base class with default fields and methods."""

    uuid: str


class BaseElasticModel(Base):
    """BaseElasticModel to get data from the ElasticSearch."""

    id: str
