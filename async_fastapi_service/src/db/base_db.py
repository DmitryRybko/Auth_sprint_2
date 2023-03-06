"""Base DB module."""

import abc

from models.films import FilmAPI, FilmAPIList
from models.genres import GenreAPI
from models.persons import PersonAPI
from models.sort import ImdbRatingFilmSort


class BaseDB():
    @abc.abstractmethod
    def get_all_films(
        page: int,
        size: int,
        sort: ImdbRatingFilmSort = None,
        genre: str = None
    ) -> list[FilmAPIList]:
        """Return all film items page-by-page.

        Args:
            page (int): Pagination page number.
            size (int): Pagination page size.
            sort (ImdbRatingFilmSort | None): sorting by film rating.
            genre (str): filter by genre.
        Returns:
            list[FilmAPIList]
        """
        pass

    @abc.abstractmethod
    def get_all_persons(
        page: int,
        size: int,
    ) -> list[PersonAPI]:
        """Return all person items page-by-page.

        Args:
            page (int): Pagination page number.
            size (int): Pagination page size.
        Returns:
            list[PersonAPI]
        """
        pass

    @abc.abstractmethod
    def get_all_genres(
        page: int,
        size: int,
    ) -> list[GenreAPI]:
        """Return all genre items page-by-page.

        Args:
            page (int): Pagination page number.
            size (int): Pagination page size.
        Returns:
            list[GenreAPI]
        """
        pass

    @abc.abstractmethod
    def get_film_by_id(uuid: str) -> FilmAPI:
        """Return film by id.

        Args:
            uuid (str): film uuid.
        Returns:
            FilmAPI
        """
        pass

    @abc.abstractmethod
    def get_person_by_id(uuid: str) -> PersonAPI:
        """Return person by id.

        Args:
            uuid (str): person uuid.
        Returns:
            PersonAPI
        """
        pass

    @abc.abstractmethod
    def get_genre_by_id(uuid: str) -> GenreAPI:
        """Return genre by id.

        Args:
            uuid (str): genre uuid.
        Returns:
            GenreAPI
        """
        pass

    @abc.abstractmethod
    def get_films_by_search(
        page: int, size: int, query: str
    ) -> list[FilmAPIList]:
        """Return films by search query.

        Args:
            page (int): Pagination page number.
            size (int): Pagination page size.
            query (str): Search query request.
        Returns:
            list[FilmAPIList]
        """
        pass

    def get_persons_by_search(
        page: int, size: int, query: str
    ) -> list[PersonAPI]:
        """Return persons by search query.

        Args:
            page (int): Pagination page number.
            size (int): Pagination page size.
            query (str): Search query request.
        Returns:
            list[PersonAPI]
        """
        pass
