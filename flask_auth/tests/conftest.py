"""Conftest file for flask_auth app tests."""

from typing import Iterator
import uuid

import psycopg2

import pytest

import requests  # type: ignore

from werkzeug.security import generate_password_hash

from flask_auth.project.settings import app_settings  # noqa: I100
from .utils import helpers
from .settings import test_settings

user_table_name: str = '"user"'
roles_table_name: str = '"role"'

address_api: str = test_settings.api_address

content_type: str = "Content-Type"
application_json: str = "application/json"


@pytest.fixture
def db_connect() -> Iterator:
    """Return postgres DB cursor to work with DB."""
    dsl: dict = {
        "dbname": app_settings.postgres_db,
        "user": app_settings.postgres_user,
        "password": app_settings.postgres_password,
        "host": app_settings.postgres_host,
        "port": int(app_settings.postgres_port),
    }
    with psycopg2.connect(**dsl) as pg_conn:
        yield pg_conn


@pytest.fixture
def admin_user(db_connect) -> Iterator:
    """Add admin user in the DB."""
    db_cursor = db_connect.cursor()
    user: dict = {
        "id": uuid.uuid4(),
        "email": helpers.get_random_email(),
        "name": helpers.get_random_string(10),
        "password": helpers.get_random_string(15),
        "is_admin": "t"
    }
    sql = (
        f"INSERT INTO {user_table_name} "
        '("id", "email", "name", "password", "is_admin") '
        f"VALUES ('{user['id']}', '{user['email']}', '{user['name']}', "
        f"'{generate_password_hash(user['password'], method='sha256')}', "
        f"'{user['is_admin']}');"
    )
    db_cursor.execute(sql)
    db_connect.commit()
    yield user
    db_cursor.execute('DELETE FROM "log_history" CASCASE;')
    db_cursor.execute(f'DELETE FROM {user_table_name} CASCADE;')
    db_connect.commit()


@pytest.fixture
def access_token_admin_user(admin_user):
    """Return access_token for admin user."""
    req = requests.post(
        f"{address_api}/auth/login",
        json={
            "email": admin_user["email"],
            "password": admin_user["password"]
        },
        headers={content_type: application_json}
    )
    access_token = req.json().get("access_token")
    yield access_token


@pytest.fixture
def access_token_regular_user(regular_user):
    """Return access_token for regular user."""
    req = requests.post(
        f"{address_api}/auth/login",
        json={
            "email": regular_user["email"],
            "password": regular_user["password"]
        },
        headers={content_type: application_json}
    )
    access_token = req.json().get("access_token")
    yield access_token


@pytest.fixture
def regular_user(db_connect) -> Iterator:
    """Add admin user in the DB."""
    db_cursor = db_connect.cursor()
    user: dict = {
        "id": uuid.uuid4(),
        "email": helpers.get_random_email(),
        "name": helpers.get_random_string(10),
        "password": helpers.get_random_string(15),
        "is_admin": "f"
    }
    sql = (
        'INSERT INTO "user" '
        '("id", "email", "name", "password", "is_admin") '
        f"VALUES ('{user['id']}', '{user['email']}', '{user['name']}', "
        f"'{generate_password_hash(user['password'], method='sha256')}', "
        f"'{user['is_admin']}');"
    )
    db_cursor.execute(sql)
    db_connect.commit()
    yield user
    db_cursor.execute('DELETE FROM "log_history" CASCASE;')
    db_cursor.execute('DELETE FROM "user" CASCADE;')
    db_connect.commit()


@pytest.fixture
def test_5_roles(db_connect) -> Iterator:
    """Add 5 roles in the DB to test."""
    db_cursor = db_connect.cursor()
    sql: str = ""
    for i in range(5):
        sql += (
            f'INSERT INTO "role" ("id", "name") VALUES '
            f"('{uuid.uuid4()}', 'test_role_{i}');"
        )

    db_cursor.execute(sql)
    db_connect.commit()
    yield
    db_cursor.execute('DELETE FROM "user_role" cascade;')
    db_cursor.execute('DELETE FROM "role" cascade;')
    db_connect.commit()
