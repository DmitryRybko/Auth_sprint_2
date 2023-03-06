"""Person model."""

from pydantic import BaseModel

from .base import BaseAPIModel, BaseElasticModel


class PersonBaseModel(BaseModel):
    full_name: str


class PersonAPI(BaseAPIModel, PersonBaseModel):
    """Model to return persons in API."""

    role: str
    # film_ids: list[str]


class PersonElastic(BaseElasticModel, PersonBaseModel):
    """Model to return persons in API."""

    roles: list
    # film_ids: list[str]
