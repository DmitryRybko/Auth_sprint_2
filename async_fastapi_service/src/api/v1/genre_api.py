"""API for /api/v1/genres."""

from logging import getLogger
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi_cache.decorator import cache

from models.genres import GenreAPI
from services.genre import GenreService, get_genre_service
from core.text_messages import text_messages

# Router object to register handlers.
router: APIRouter = APIRouter()

logger = getLogger(__name__)

@router.get('/', response_model=list[GenreAPI])
@cache(expire=120)
async def genre_list(
    page: int = Query(default=1, ge=1, le=100, alias='page[number]'),
    size: int = Query(default=10, ge=1, le=100, alias='page[size]'),
    genre_service: GenreService = Depends(get_genre_service)
) -> list[GenreAPI]:
    """Returns the list of all genres from the database.

    Args:
        page (int): Pagination page number.
        size (int): Pagination page size.
        genre_service (GenreService): item of GenreService class.
    Returns:
        list[GenreAPI]
    """
    logger.debug(f'Getting genre list; page: {page}; page size: {size})')

    genre_list: list[GenreAPI] = await genre_service.get_all(
        page, size
    )

    if not genre_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages["genre_not_found"]
        )

    return genre_list


@router.get('/{genre_id}', response_model=GenreAPI)
@cache(expire=120)
async def genre_details(
    genre_id: str = Path(max_length=50, min_length=5),
    genre_service: GenreService = Depends(get_genre_service)
) -> GenreAPI:
    """Returns detailed information about a genre based on id provided.

    Args:
        genre_id (str): genre uuid
        genre_service (GenreService): item of GenreService class.
    Returns:
        GenreAPI
    """
    logger.debug(f'Get genre by id. ID: {genre_id};')

    genre: GenreAPI = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages["genre_not_found"]
        )
    return genre
