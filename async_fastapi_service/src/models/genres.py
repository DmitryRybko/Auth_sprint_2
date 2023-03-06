"""Genre model."""

from pydantic import BaseModel

from .base import BaseAPIModel, BaseElasticModel


class BaseGenreModel(BaseModel):
    """Base model for genre."""

    name: str
    description: str


class GenreAPI(BaseAPIModel, BaseGenreModel):
    """Model to return genres in API."""

    uuid: str
    name: str


class GenreElasticModel(BaseElasticModel, BaseGenreModel):
    """Model to get data from Elasticsearch."""

    id: str
    name: str
