"""Base service module."""

import abc
from typing import Any

from db.base_db import BaseDB


class BaseService(abc.ABC):
    """Abstract class to create interface for all services."""

    @abc.abstractmethod
    def __init__(self, db: BaseDB):
        """Init class."""
        self.db = db

    @abc.abstractmethod
    def get_all(self, page: int, size: int) -> Any:
        """Return all items separated by pages."""
        pass

    @abc.abstractmethod
    def get_by_id(self, uuid: str) -> Any:
        """Return item by uuid."""
        pass
