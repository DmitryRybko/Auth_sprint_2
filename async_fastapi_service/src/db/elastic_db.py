"""Elastic DB module."""

import json

from logging import getLogger
from typing import Any

from elasticsearch7 import AsyncElasticsearch, NotFoundError

from db.base_db import BaseDB
from models.films import FilmAPI, FilmAPIList, FilmElastic
from models.genres import GenreAPI, GenreElasticModel
from models.persons import PersonAPI, PersonElastic
from models.sort import ImdbRatingFilmSort


logger = getLogger(__name__)


class ElasticDB(BaseDB):
    def __init__(self, elastic: AsyncElasticsearch):
        """Init ElasticDB class.

        Args:
            elastic (AsyncElasticsearch): item to work with elastic.
        Return:
            None
        """
        self.elastic: AsyncElasticsearch = elastic
        self.index_films: str = 'film_work'
        self.index_genres: str = 'genres'
        self.index_persons: str = 'persons'

    async def get_all_films(
        self,
        page: int,
        size: int,
        genre: str | None = None,
        sort: ImdbRatingFilmSort | None = None
    ) -> list[FilmAPIList]:
        """Return part of all films.

        Args:
            page (int): page number.
            size (int): number items on page.
            genre (str | None): Genre to filter.
            sort (ImdbRatingFilmSort | None): sort by rating.
        Returns:
            list[FilmAPIList]
        """
        logger.info('Elastic all films request')

        if genre:
            logger.info(f'Genre: {genre}')
            query = {
                'bool': {
                    'should': [{'term': {'genre': genre}}]
                }
            }
        else:
            query = {'match_all': {}}

        if sort:
            if sort == ImdbRatingFilmSort.imdb_rating:
                sort_body = {'imdb_rating': 'asc'}
            elif sort == ImdbRatingFilmSort.imdb_rating_revert:
                sort_body = {'imdb_rating': 'desc'}
            else:
                sort_body = {}
        else:
            sort_body = {}

        films: list[FilmElastic] = await self._search_in_films_index({
                'from': ((page - 1) * size),
                'size': size,
                'sort': [sort_body,],
                'query': query
            }
        )
        logger.info(f'Request returned {len(films)} films')
        return [
            FilmAPIList(
                uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating
            ) for film in films
        ]

    async def get_all_genres(self, page: int, size: int) -> list[GenreAPI]:
        """Return part of all genres.

        Args:
            page (int): page number.
            size (int): number items on page.
        Returns:
            list[GenreAPI]
        """
        genres: list[GenreElasticModel] = []
        try:
            genres = await self._search_in_genres_index(
                body={
                    'from': ((page - 1) * size),
                    'size': size,
                    'query': {'match_all': {}}
                }
            )
        except NotFoundError:
            return None
        if len(genres) == 0:
            return None
        return [
            GenreAPI(
                uuid=genre.id, name=genre.name, description=genre.description
            ) for genre in genres
        ]

    async def get_all_persons(self, page: int, size: int) -> list[PersonAPI]:
        """Return part of all persons.

        Args:
            page (int): page number.
            size (int): number items on page.
        Returns:
            list[PersonAPI]
        """
        try:
            persons: list[PersonElastic] = await self._search_in_persons_index(
                {
                    'from': ((page - 1) * size),
                    'size': size,
                    'query': {'match_all': {}}
                }
            )
        except NotFoundError:
            return None
        if len(persons) == 0:
            return None

        return [
            PersonAPI(
                uuid=p.id,
                full_name=p.full_name,
                role=p.roles,
                film_ids=p.film_ids
            ) for p in persons
        ]
        result: list[PersonAPI] = [
            self.get_person_by_id(p.id) for p in persons
        ]
        return result

    async def get_film_by_id(self, uuid: str) -> FilmAPI:
        """Return film by id.

        Args:
            uuid (str): film UUID.
        Returns:
            FilmAPI
        """
        try:
            doc: dict = await self.elastic.get(self.index_films, uuid)
        except NotFoundError:
            return None
        film: FilmElastic = FilmElastic(**doc['_source'])
        return FilmAPI(
            uuid=film.id,
            title=film.title,
            description=film.description,
            imdb_rating=film.imdb_rating,
            genre=[{'name': g} for g in film.genre],
            actors=film.actors,
            writers=film.writers,
            directors=film.director
        )

    async def get_films_by_search(
        self, page: int, size: int, query: str
    ) -> list[FilmAPIList] | None:
        """Return film list by search query.

        Args:
            page (int): Pagination page num.
            size (int): Pagination page size.
            query (str): Search query request.
        Returns:
            list[FilmAPIList]
        """
        try:
            films: list[FilmElastic] = await self._search_in_films_index(
                body={
                    'from': ((page - 1) * size),
                    'size': size,
                    'query': {'query_string': {'query': query}}
                }
            )
        except NotFoundError:
            return None
        if len(films) == 0:
            return None

        return [
            FilmAPIList(
                uuid=film.id, title=film.title, imdb_rating=film.imdb_rating
            ) for film in films
        ]

    async def get_person_by_id(self, uuid: str) -> PersonAPI:
        """Return person by id.

        Args:
            uuid (str): person uuid.
        Returns:
            PersonAPI
        """
        try:
            doc = await self.elastic.get(self.index_persons, uuid)
        except NotFoundError:
            return None
        person = PersonElastic(**doc['_source'])
        if not person:
            return None

        return PersonAPI(
            uuid=person.id,
            full_name=person.full_name,
            role=', '.join(person.roles),
            # film_ids=person.film_ids
        )

    async def _get_films_by_person_id(
        self, person_id: str
    ) -> list[FilmAPIList]:
        """Return films by person id.

        Args:
            person_id (str): person uuid.
        Returns:
            list[FilmAPIList]
        """
        return await self._search_in_films_index(
            body={
                'query': {
                    'bool': {
                        'should': [
                            {
                                'nested': {
                                    'path': 'actors',
                                    'ignore_unmapped': True,
                                    'query': {
                                        'term': {
                                            'actors.id': {'value': person_id}
                                        }
                                    }
                                }
                            },
                            {
                                'nested': {
                                    'path': 'writers',
                                    'ignore_unmapped': True,
                                    'query': {
                                        'term': {
                                            'writers.id': {'value': person_id}
                                        }
                                    }
                                },
                            },
                            {
                                'match': {
                                    'director': {
                                        'query': person_id,
                                        'operator': 'and'
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )

    async def get_genre_by_id(self, uuid: str) -> GenreAPI:
        """Return genre by id.

        Args:
            uuid (str): genre id.
        Returns:
            GenreAPI
        """
        try:
            doc: dict = await self.elastic.get(self.index_genres, uuid)
        except NotFoundError:
            return None
        genre: GenreElasticModel = GenreElasticModel(**doc['_source'])
        return GenreAPI(
            uuid=genre.id, name=genre.name, description=genre.description
        )

    async def get_persons_by_search(
        self, page: int, size: int, query: str
    ) -> list[PersonAPI]:
        """Return person by search query.

        Args:
            page (int): Pagination page num.
            size (int): Pagination page size.
            query (str): Search query.
        Returns:
            list[PersonAPI]
        """
        try:
            persons: list[PersonElastic] = await self._search_in_persons_index(
                body={
                    'from': ((page - 1) * size),
                    'size': size,
                    'query': {'query_string': {'query': query}}
                }
            )
        except NotFoundError:
            return None
        if len(persons) == 0:
            return None
        return [
            await self.get_person_by_id(p.id) for p in persons
        ]

    async def _search_in_films_index(self, body: dict) -> list[FilmElastic]:
        """Return search response from films index.

        Args:
            body (dict): body to request in ElasticSearch.
        Returns:
            list[FilmElastic]
        """
        return await self._get_search_request(
            self.index_films, body, FilmElastic
        )

    async def _search_in_genres_index(
        self, body: dict
    ) -> list[GenreElasticModel]:
        """Return search response from genres index.

        Args:
            body (dict): body to request in ElasticSearch.
        Returns:
            list[GenreElasticModel]
        """
        return await self._get_search_request(
            self.index_genres, body, GenreElasticModel
        )

    async def _search_in_persons_index(
        self, body: dict
    ) -> list[PersonElastic]:
        """Return search response from persons index.

        Args:
            body (dict): body to request in ElasticSearch.
        Returns:
            list[PersonElastic]
        """
        return await self._get_search_request(
            self.index_persons, body, PersonElastic
        )

    async def _get_search_request(
        self, index: str, body: dict, model: Any
    ) -> Any:
        """Return search response in ElasticSearch.

        Args:
            index (str): index name.
            body (dict): body to request in ElasticSearch.
            model (Any): data model to return.
        Returns:
            Any
        """
        res: dict = await self.elastic.search(index=index, body=body)
        return [model(**d['_source']) for d in res['hits']['hits']]
