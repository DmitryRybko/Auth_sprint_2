"""Config module for FastAPI project."""

import os
from pydantic import BaseSettings
from logging import config as logging_config
from dotenv import load_dotenv

from .logger import LOGGING

# load_dotenv здесь нужен несмотря на наличие pydantic, так как pydantic не умеет искать env в parent директориях
load_dotenv()


logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):

    PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

    DB_NAME: str = "movies_database"
    DB_USER: str = "some_user"
    DB_PASSWORD: str = "some_password"
    SECRET_KEY: str = "some_secret_key"
    DSN_OPTIONS = '-c search_path=content'

    DB_HOST: str = "localhost"
    DB_PORT: int = 54321

    ELASTIC_HOST = os.getenv('ES_HOST', '127.0.0.1')
    ELASTIC_PORT = int(os.getenv('ES_PORT', 9200))

    INDEX_NAME: str = "film_work"
    INDEX_NAME_GENRE: str = "genres"
    INDEX_NAME_PERSONS: str = "persons"

    STARTING_TIME: str = "2000-06-16 23:14:09.200 +0300"

    STATE_STORAGE_FILE: str = "state_file.txt"

    ETL_SLEEP_TIME: int = 10

    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        case_sensitive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
