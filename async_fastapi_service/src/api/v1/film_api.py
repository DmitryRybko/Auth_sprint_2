"""Films module for fastapi API requests.

/api/v1/films?sort=-imdb_rating
/api/v1/films?sort=-imdb_rating&filter[genre]=<comedy-uuid>
/api/v1/films/search/
"""

from http import HTTPStatus
from logging import getLogger
import random

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

from fastapi_cache.decorator import cache

from typing import List
from pydantic import BaseModel
from uuid import UUID, uuid4

from models.films import FilmAPI, FilmAPIList, GenresOfFilmsAPIList, GenresOfFilmsAPIListRequest
from models.sort import ImdbRatingFilmSort
from core.text_messages import text_messages

from services.film import FilmService, get_film_service


logger = getLogger(__name__)

# Router object to register handlers.
router = APIRouter()


@router.get('/search', response_model=list[FilmAPIList])
@cache(expire=120)
async def film_search(
        search_line: str = Query(min_length=1, max_length=255, alias='query'),
        page: int = Query(default=1, ge=1, le=100, alias='page[number]'),
        size: int = Query(default=10, ge=1, le=100, alias='page[size]'),
        film_service: FilmService = Depends(get_film_service)
) -> list[FilmAPIList]:
    """Return the list of all movies meeting the search criteria (split by page).

    It is possible to indicate number of results per page.

    Args:
        search_line (str): Query search request.
        page (int): Pagination page number.
        size (int): Pagination page size.
        film_service (FilmService): Service to get data.
    Returns:
        list[FilmAPIList]
    """
    logger.debug(
        (
            'Request to film_search. '
            f'Search line: {search_line}; page: {page}; size: {size}'
        )
    )
    film_list: list[FilmAPIList] = await film_service.get_by_search(
        search_line,
        page,
        size
    )

    if not film_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages['empty_film_list']
        )

    return film_list


@router.get('/', response_model=list[FilmAPIList])
@cache(expire=120)
async def film_list(
    genre: str | None = Query(
        default=None, min_length=3, max_length=50, alias='filter[genre]'
    ),
    sort: ImdbRatingFilmSort | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=100, alias='page[number]'),
    size: int = Query(default=10, ge=1, le=100, alias='page[size]'),
    film_srv: FilmService = Depends(get_film_service),
) -> list[FilmAPIList]:
    """Returns the list of all movies from the database (split by page).

    It is possible to narrow the search by a genre,
    sort the results by IMDB rating (ascending and descending),
    and indicate number of results per page.

    Args:
        genre (str | None): Filter by genre.
        sort (ImdbRatingFilmSort | None): Sorting by rating.
        page (int): Pagination page number.
        size (int): Pagination page size.
        film_srv (FilmService): Service to get data.
    Returns:
        list[FilmAPIList]
    """
    logger.debug(
        (
            'Request to film_list. '
            f'Genre: {genre}; sort: {sort}; page: {page}; size: {size}'
        )
    )

    all_movies: list[FilmAPIList] = await film_srv.get_all(
        page, size, sort, genre
    )

    if not all_movies:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages['empty_film_list']
        )

    return all_movies


@router.get('/{film_id}', response_model=FilmAPI)
@cache(expire=120)
async def film_details(
    film_id: str = Path(title='Film UUID', max_length=50, min_length=5),
    film_srv: FilmService = Depends(get_film_service)
) -> FilmAPI:
    """Returns detailed information about a movie based on id provided.

    Args:
        film_id (str): film UUID.
        film_srv (FilmService): service to get a film.

    Returns:
        list[FilmAPI]
    """
    logger.debug(f'Request to film_details. Film UUID: {film_id}')
    film: FilmAPI = await film_srv.get_by_id(film_id)

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages["film_not_found"]
        )

    return film


@router.post("/get_genres", response_model=GenresOfFilmsAPIList)
async def get_genres(request: GenresOfFilmsAPIListRequest):
    print(request.movies)

    try:
        genres = []
        for movie in request.movies:
            genre = random.choice(["action", "sci-fi", "comedy"])
            genres.append(genre)
        response = GenresOfFilmsAPIList(genre_ids=genres)
        return response
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
