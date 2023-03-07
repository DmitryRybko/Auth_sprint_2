"""Module for support sort models."""

from enum import Enum


class ImdbRatingFilmSort(str, Enum):
    """Model for sort values."""

    imdb_rating = '+imdb_rating'
    imdb_rating_revert = '-imdb_rating'
