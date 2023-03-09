"""Functional test for flask_auth app."""

from http import HTTPStatus

import requests  # type: ignore

from ..settings import test_settings
from ..utils import helpers

address_api: str = test_settings.api_address

test_email: str = helpers.get_random_email()
test_password: str = helpers.get_random_string(15)
test_name: str = helpers.get_random_string(5)

content_type: str = "content_type"
application_json: str = "application/json"


def test_user_crud():
    """Test User CRUD.

    Test case:
        register new user
        try to login with wrong data
        login as the user
        try to see user profile without access token
        try to see user profile with wrong token
        get user profile
        update user data
        logout
        try to see user profile with logouted token

    Args:
        -
    Returns:
        None
    """
    # create new user
    req = requests.post(
        f"{address_api}/auth/register",
        json={
            "email": test_email, "password": test_password, "name": test_name
        },
        headers={content_type: application_json}
    )

    assert req.status_code == HTTPStatus.OK

    # login with wrong data
    req = requests.post(
        f"{address_api}/auth/login",
        json={"email": test_email, "password": "123"},
        headers={content_type: application_json}
    )

    assert req.status_code == HTTPStatus.UNAUTHORIZED
    assert not req.json().get("access_token", "")
    assert not req.json().get("refresh_token", "")
    assert req.json().get("msg") == "Bad username or password"

    # login with right data
    req = requests.post(
        f"{address_api}/auth/login",
        json={"email": test_email, "password": test_password},
        headers={content_type: application_json}
    )
    assert req.status_code == HTTPStatus.OK
    assert req.json().get("access_token", "")
    assert req.json().get("refresh_token", "")

    access_token: str = req.json().get("access_token", "")
    refresh_token: str = req.json().get("refresh_token", "")

    # see profile without token
    req = requests.get(
        f"{address_api}/auth/profile",
        headers={content_type: application_json}
    )
    assert req.status_code == HTTPStatus.UNAUTHORIZED
    assert req.json().get("msg", "") == "Missing Authorization Header"

    # see profile with bad token
    req = requests.get(
        f"{address_api}/auth/profile",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {refresh_token}"
        }
    )
    assert req.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # see profile with right token
    req = requests.get(
        f"{address_api}/auth/profile",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert req.status_code == HTTPStatus.OK
    assert req.json().get("name", "") == test_name
    assert req.json().get("id", "")
    assert req.json().get("email", "") == test_email

    # update data
    new_name: str = helpers.get_random_string(7)
    req = requests.patch(
        f"{address_api}/auth/profile",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token}"
        },
        json={"name": new_name}
    )
    assert req.status_code == 200

    req = requests.get(
        f"{address_api}/auth/profile",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert req.status_code == HTTPStatus.OK
    assert req.json().get("name", "") == new_name

    # logout
    req = requests.post(
        f"{address_api}/auth/logout",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token}"
        }
    )
    req.status_code == HTTPStatus.OK

    req = requests.get(
        f"{address_api}/auth/profile",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert req.status_code == HTTPStatus.UNAUTHORIZED
