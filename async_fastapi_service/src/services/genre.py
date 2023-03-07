"""Module to get data about genres."""

from functools import lru_cache

from fastapi import Depends

from models.genres import GenreAPI

from services.base_service import BaseService

from db.base_db import BaseDB
from db.db_getter import get_db


class GenreService(BaseService):
    """Genre service to work with genres."""

    def __init__(self, db: BaseDB) -> None:
        """Init GenreService.

        Args:
            db (BaseDB): db item to get data.
        Returns:
            None
        """
        self.db = db

    async def get_by_id(self, uuid: str) -> GenreAPI | None:
        """Return genre by uuid.

        Args:
            uuid (str): UUID to get a genre.
        Returns:
            GenreAPI
        """
        return await self.db.get_genre_by_id(uuid)

    async def get_all(self, page: int, size: int) -> list[GenreAPI] | None:
        """Return all genres separated by page.

        Args:
            page (int): Pagination page number.
            size (int): Pagination page size.
        Returns:
            list[GenreAPI]
        """
        return await self.db.get_all_genres(page, size)


@lru_cache()
def get_genre_service(
        db: BaseDB = Depends(get_db)
) -> GenreService:
    """Return GenreService item.

    Args:
        db (BaseDB): DB item to get data.
    Returns:
        GenreService
    """
    return GenreService(db)
