"""Film service module."""

from functools import lru_cache
from logging import getLogger

from fastapi import Depends

from db.base_db import BaseDB
from db.db_getter import get_db
from utils.helpers import clear_search_query
from models.films import FilmAPI, FilmAPIList
from models.genres import GenreAPI
from models.sort import ImdbRatingFilmSort
from services.base_service import BaseService

logger = getLogger(__name__)


class FilmService(BaseService):

    def __init__(self, db: BaseDB) -> None:
        self.db: BaseDB = db

    async def get_all(
        self,
        page: int = 1,
        size: int = 10,
        sort: ImdbRatingFilmSort | None = None,
        genre_id: str | None = None
    ) -> list[FilmAPIList]:
        """Return part of films.
        Args:
            page (int): page number.
            size (int): number of items in response.
            sort (ImdbRatingSort): param to sort films by rating.
            genre_id (str): param to filter films by genre.
        Returns:
            list[FilmAPIList]
        """
        logger.info(
            (
                'Getting all films. Params: '
                f'page: {page}; size: {size}; sort: {sort}; genre: {genre_id}'
            )
        )
        if genre_id:
            genre: GenreAPI = await self.db.get_genre_by_id(genre_id)
            if not genre:
                return None
            genre_for_search: str | None = genre.name
        else:
            genre_for_search = None
        return await self.db.get_all_films(
            page=page, size=size, sort=sort, genre=genre_for_search
        )

    async def get_by_id(self, uuid: str) -> FilmAPI:
        """Return film by UUID.

        Args:
            uuid (str): UUID of a film.
        Returns:
            FilmAPI
        """
        logger.info(f'Getting film by UUID: {uuid}')
        return await self.db.get_film_by_id(uuid)

    async def get_by_search(
        self, query: str, page: int = 1, size: int = 50
    ) -> list[FilmAPIList]:
        """Return part of films by query search.

        Args:
            page (int): page number.
            size (int): number of items in response.
            query (str): query request.
        Returns:
            list[FilmAPIList]
        """
        query = clear_search_query(query)
        logger.info(
            (
                'Getting films by search. '
                f'Params: page: {page}; size: {size}; query: {query}'
            )
        )
        return await self.db.get_films_by_search(
            page=page, size=size, query=query
        )


# get_film_service is provider of FilmService.
# Using Depends it informs that it needs Elasticsearch
# For obtaining Elasticsearch there are provider-functions in db module.
# lru_cache-decorator is used to create a single service object (singleton)
@lru_cache()
def get_film_service(db: BaseDB = Depends(get_db)) -> FilmService:
    """Return sevice item to get data about films.

    Args:
        db (BaseDB): db to get data.
    Returns:
        FilmService
    """
    return FilmService(db)
