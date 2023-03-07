"""API for /api/v1/persons."""

from logging import getLogger
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from fastapi_cache.decorator import cache

from models.films import FilmAPIList
from models.persons import PersonAPI

from services.person import PersonService, get_person_service
from core.text_messages import text_messages

# Router object to register handlers.
router = APIRouter()

logger = getLogger(__name__)


@router.get('/search', response_model=list[PersonAPI])
@cache(expire=120)
async def person_search(
    query: str = Query(min_length=1, max_length=255),
    page: int = Query(default=1, ge=1, le=100, alias='page[number]'),
    size: int = Query(default=10, ge=1, le=100, alias='page[size]'),
    person_service: PersonService = Depends(get_person_service)
) -> list[PersonAPI]:
    """Return the list of all persons meeting the search criteria (split by page).

    Args:
        query (str): Query search requets.
        page (int): Pagination page number.
        size (int): Pagination page size.
        person_service (PersonService): Service item to get data.
    Returns:
        list[PersonAPI]
    """
    logger.debug('Get persons by search.')
    person_list: list[PersonAPI] = await person_service.get_by_search(
        query=query,
        page=page,
        size=size
    )

    if not person_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages["empty_person_list"]
        )

    return person_list


@router.get('/{person_id}', response_model=PersonAPI)
@cache(expire=120)
async def person_details(
    person_id: str = Path(title='Person UUID', min_length=3, max_length=50),
    person_service: PersonService = Depends(get_person_service)
) -> PersonAPI:
    """Returns detailed information about a person based on id provided.

    Args:
        person_id (str): person id to search.
        person_service (PersonService): service to get data.
    Returns:
        PersonAPI
    """
    logger.debug(f'Getting person details. Person ID: {person_id}')
    person: PersonAPI = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages["person_not_found"]
        )

    return person


@router.get('/{person_id}/film', response_model=list[FilmAPIList])
@cache(expire=120)
async def films_by_person(
    person_id: str = Path(title='Person UUID', min_length=3, max_length=50),
    person_srv: PersonService = Depends(get_person_service)
) -> list[FilmAPIList]:
    """Returns the list of all movies where a person was involved.

    Args:
        person_id (str): person id to get films.
        person_srv (PersonService): service to get films.
    Returns:
        list[FilmAPIList]
    """
    logger.debug(f'Get films by person. Person ID: {person_id}')
    film_list: list[FilmAPIList] = await person_srv.get_film_list_for_a_person(
        person_id
    )

    if not film_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=text_messages["empty_film_list"]
        )

    return film_list
