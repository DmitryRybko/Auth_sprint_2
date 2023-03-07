"""Services to get Persons objects."""

from functools import lru_cache
from logging import getLogger

from fastapi import Depends

from db.base_db import BaseDB
from db.db_getter import get_db
from models.films import FilmAPI, FilmAPIList
from models.persons import PersonAPI
from services.base_service import BaseService
from utils.helpers import clear_search_query

logger = getLogger(__name__)


class PersonService(BaseService):
    def __init__(self, db: BaseDB) -> None:
        """Init PersonService.

        Args:
            db (BaseDB): db item to get data.
        Returns:
            None
        """
        self.db: BaseDB = db

    async def get_all(self, page: int = 1, size: int = 10) -> list[PersonAPI]:
        """Return all persons separated by page.

        Args:
            page (int): Pagination page number.
            size (int): Pagination page size.
        Returns:
            list[PersonAPI]
        """
        return await self.db.get_all_persons(page=page, size=size)

    async def get_by_id(self, uuid: str) -> PersonAPI:
        """Return person by uuid.

        Args:
            uuid (str): person uuid.
        Returns:
            PersonAPI
        """
        return await self.db.get_person_by_id(uuid)

    async def get_by_search(
        self, query: str, page: int = 1, size: int = 10
    ) -> PersonAPI:
        """Return person list by search request.

        Args:
            query (str): Search query.
            page (int): Pagination page number.
            size (int): Pagination page size.
        Returns:
            PersonAPI
        """
        query: str = clear_search_query(query)
        return await self.db.get_persons_by_search(
            page=page, size=size, query=query
        )

    async def get_film_list_for_a_person(
        self, person_uuid: str
    ) -> list[FilmAPIList]:
        """Return list of films by person.

        Args:
            person_uuid (str): person id to filter films.
        Returns:
            list[FilmAPIList]
        """
        person: PersonAPI = await self.db.get_person_by_id(person_uuid)

        if not person:
            return None

        films: list[FilmAPI] = [
            await self.db.get_film_by_id(f) for f in person.film_ids
        ]
        return [
            FilmAPIList(
                uuid=f.uuid, title=f.title, imdb_rating=f.imdb_rating
            ) for f in films
        ]


@lru_cache()
def get_person_service(
    db: BaseDB = Depends(get_db)
) -> PersonService:
    """Return PersonService object.

    Args:
        db (BaseDB): db item to get data.
    Returns:
        PersonService
    """
    return PersonService(db)
