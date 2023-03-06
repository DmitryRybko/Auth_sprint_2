"""Module for Film model."""
# FastAPI uses pydantic lib for models description.
# https://pydantic-docs.helpmanual.io

from pydantic import BaseModel

from .base import BaseAPIModel, BaseElasticModel


class BaseFilmModel(BaseModel):
    """Base Film model."""

    title: str
    imdb_rating: float


class FilmElastic(BaseElasticModel, BaseFilmModel):
    """Model to work with data from ElasticSearch."""

    description: str
    director: str
    actors: list
    genre: list
    writers: list

    # These fields (actors and writers names) are presented in Elastic schema.
    # So I think we should keep them here.
    # actors_names: list
    # writers_names: list


class FilmAPI(BaseAPIModel, BaseFilmModel):
    """Model to return in API."""

    description: str
    genre: list[dict]
    actors: list[dict]
    writers: list[dict]
    directors: str


class FilmAPIList(BaseAPIModel, BaseFilmModel):
    """Model to return list of films in API."""
