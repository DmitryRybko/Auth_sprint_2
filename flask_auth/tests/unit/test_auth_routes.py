"""Tests for /auth."""

from http import HTTPStatus

import pytest

import requests  # type: ignore

from ..settings import test_settings

address_api: str = test_settings.api_address

content_type: str = "Content-Type"
application_json: str = "application/json"


def test_login(regular_user: dict) -> None:
    """Test POST /auth/login.

    Check that user can login by /auth/login.

    Args:
        regular_user (dict): existing user in the db.
    Returns:
        None
    """
    req = requests.post(
        f"{address_api}/auth/login",
        json={
            "email": "test",
            "password": "test"
        },
        headers={content_type: application_json}
    )
    assert req.status_code == HTTPStatus.UNAUTHORIZED

    req = requests.post(
        f"{address_api}/auth/login",
        headers={content_type: application_json}
    )
    assert req.status_code == HTTPStatus.BAD_REQUEST

    req = requests.post(
        f"{address_api}/auth/login",
        json={
            "email": regular_user["email"],
            "password": regular_user["password"]
        },
        headers={content_type: application_json}
    )
    assert req.status_code == HTTPStatus.OK, req.text


@pytest.mark.parametrize(
    "email, password, name, result",
    (
        ("some@test.com", "password", "test_name", HTTPStatus.OK),
        ("", "password", "test_name", HTTPStatus.BAD_REQUEST),
        ("test@test.local", "", "test_name", HTTPStatus.BAD_REQUEST),
        ("test@test.com", "password", "", HTTPStatus.OK)
    )
)
def test_register(
    regular_user: dict,
    email: str,
    password: str,
    name: str,
    result: HTTPStatus
) -> None:
    """Test POST /auth/register.

    Check that a user can register in the service.

    Args:
        regular_user (dict): prepared user in the db.
        email (str): test email from pytest params.
        password (str): test password from pytest params.
        name (str): test name from pytest params.
        result (HTTPStatus): result status to check.
    """
    req = requests.post(
        f"{address_api}/auth/register",
        json={"email": email, "password": password, "name": name},
        headers={content_type: application_json}
    )
    assert req.status_code == result, req.text


def test_profile(
    access_token_regular_user: str, access_token_admin_user: str
) -> None:
    """Test GET /auth/profile.

    Check that user can get its data.

    Args:
        access_token_admin_user (str): Access token to get profile of admin.
        access_token_regular_user (str): Access token to get profile of user.
    Returns:
        None
    """
    for token in (access_token_admin_user, access_token_regular_user):
        req = requests.get(
            f"{address_api}/auth/profile",
            headers={
                content_type: application_json,
                "Authorization": f"Bearer {token}"
            }
        )
        assert req.status_code == HTTPStatus.OK, req.text
        assert req.json()["name"], req.text
        assert req.json()["id"], req.text
        assert req.json()["email"], req.text


def test_profile_patch(regular_user: dict) -> None:
    """Test PATCH /auth/profile.

    Check that user can update its data.

    Args:
        regular_user (dict): Prepared user from the db.
    Returns:
        None
    """
    req = requests.post(
        f"{address_api}/auth/login",
        json={
            "email": regular_user["email"],
            "password": regular_user["password"]
        },
        headers={content_type: application_json}
    )
    access_token: str = req.json().get("access_token")
    req = requests.patch(
        f"{address_api}/auth/profile",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "name": "new name",
            "password": "new-password"
        }
    )
    assert req.status_code == HTTPStatus.OK, req.text


def test_logout(
    access_token_regular_user: str, access_token_admin_user: str
) -> None:
    """Test POST /auth/logut.

    Check that user can logout.

    Args:
        access_token_regular_user (str): Access token for regular user.
        access_token_admin_user (str): Access token for admin user.
    Returns:
        None
    """
    for token in (access_token_admin_user, access_token_regular_user):
        req = requests.post(
            f"{address_api}/auth/logout",
            headers={
                content_type: application_json,
                "Authorization": f"Bearer {token}"
            }
        )
        assert req.status_code == HTTPStatus.OK, req.text
        req = requests.get(
            f"{address_api}/auth/profile",
            headers={
                content_type: application_json,
                "Authorization": f"Bearer {token}"
            }
        )
        assert req.status_code == HTTPStatus.UNAUTHORIZED, req.text


def test_set_admin(
    access_token_admin_user: str,
    regular_user: dict,
    access_token_regular_user: str
) -> None:
    """Test PATCH /auth/set_admin.

    Check that admin can get admin rigts for a regular user.

    Args:
        access_token_admin_user (str): Access token of admin user.
        regular_user (dict): Prepared regular user from the db.
        access_token_regular_user (str): Access token of regular user.
    Returns:
        None
    """
    # check that regular user cannot add rights.
    req = requests.patch(
        f"{address_api}/auth/set_admin",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_regular_user}"
        },
        json={"email": regular_user["email"], "is_admin": "True"}

    )
    assert req.status_code != HTTPStatus.OK, req.text

    # check that admin can add rights.
    req = requests.patch(
        f"{address_api}/auth/set_admin",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"], "is_admin": "True"}
    )
    assert req.status_code == HTTPStatus.OK, req.text


@pytest.mark.parametrize(
    "route", ("/auth/login", "/auth/logout", "/auth/register")
)
def test_users_wrong_get_routes(route: str):
    """Check that GET method is not allowed for the routes.

    Args:
        route (str): prepared route that should not have GET method.
    Returns:
        None
    """
    req = requests.get(
        f"{address_api}{route}",
        headers={content_type: application_json}
    )
    assert req.status_code == HTTPStatus.METHOD_NOT_ALLOWED, req.text
