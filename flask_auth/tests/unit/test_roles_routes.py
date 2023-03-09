"""Tests for /roles."""

from http import HTTPStatus

import pytest

import requests  # type: ignore

from ..settings import test_settings

address_api: str = test_settings.api_address

content_type: str = "Content-Type"
application_json: str = "application/json"


def test_create_role(access_token_admin_user: str) -> None:
    """Test POST /roles/create.

    Check that admin can create new role.

    Args:
        access_token_admin_user (str): Access token of admin user.
    Returns:
        None
    """
    req = requests.post(
        f"{address_api}/roles/create",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"name": "test role"}
    )
    assert req.status_code == HTTPStatus.OK, req.text


def test_delete_role(test_5_roles: None, access_token_admin_user: str) -> None:
    """Test DELETE /roles/delete.

    Check that admin can delete a role.

    Args:
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
        access_token_admin_user (str): Access token of admin user.
    Returns:
        None
    """
    req = requests.get(
        f"{address_api}/roles/all",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        }
    )
    role = req.json()[1]
    req = requests.delete(
        f"{address_api}/roles/delete",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"name": role["name"]}
    )
    assert req.status_code == HTTPStatus.OK, req.text


def test_update_role(test_5_roles: None, access_token_admin_user: str) -> None:
    """Test PATCH /roles/update.

    Check that admin can update data about a role.

    Args:
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
        access_token_admin_user (str): Access token of admin user.
    Returns:
        None
    """
    req = requests.get(
        f"{address_api}/roles/all",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        }
    )
    role = req.json()[1]
    req = requests.patch(
        f"{address_api}/roles/update",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"name": role["name"], "new_name": "new test role"}
    )
    assert req.status_code == HTTPStatus.OK, req.text


def test_all_roles(access_token_admin_user: str, test_5_roles: None) -> None:
    """Test GET /roles/all.

    Check that admin can get all roles.

    Args:
        access_token_admin_user (str): Access token of admin user.
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
    Returns:
        None
    """
    req = requests.get(
        f"{address_api}/roles/all",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        }
    )
    assert req.status_code == HTTPStatus.OK, req.text
    assert len(req.json()) == 5, req.text


def test_set_role(
    access_token_admin_user: str, regular_user: dict, test_5_roles: None
) -> None:
    """Test PATCH /roles/set_role.

    Check that admin can set role for a regular user.

    Args:
        access_token_admin_user (str): Access token of admin user.
        regular_user (dict): Prepared regular user in the db.
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
    Returns:
        None
    """
    req = requests.get(
        f"{address_api}/roles/all",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        }
    )
    role: dict = req.json()[0]
    req = requests.patch(
        f"{address_api}/roles/set_role",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"], "role": role["name"]}
    )
    assert req.status_code == HTTPStatus.OK, req.text


def test_remove_role(
    access_token_admin_user: str, regular_user: dict, test_5_roles: None
) -> None:
    """Test PATCH /roles/remove_role.

    Check that admin can remove a role from a regular user.

    Args:
        access_token_admin_user (str): Access token of admin user.
        regular_user (dict): Prepared regular user from the db.
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
    Returns:
        None
    """
    req = requests.get(
        f"{address_api}/roles/all",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        }
    )
    role = req.json()[0]
    req = requests.patch(
        f"{address_api}/roles/set_role",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"], "role": role["name"]}
    )
    req = requests.patch(
        f"{address_api}/roles/remove_role",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"], "role": role["name"]}
    )
    assert req.status_code == HTTPStatus.OK, req.text


def test_user_roles(
    access_token_admin_user: str, regular_user: dict, test_5_roles: None
) -> None:
    """Test POST /roles/user_roles.

    Check that admin can get role list for a user.

    Args:
        access_token_admin_user (str): Access token of admin user.
        regular_user (dict): Prepared regular user from the db.
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
    Returns:
        None
    """
    req = requests.get(
        f"{address_api}/roles/all",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        }
    )
    for role in req.json():
        req = requests.patch(
            f"{address_api}/roles/set_role",
            headers={
                content_type: application_json,
                "Authorization": f"Bearer {access_token_admin_user}"
            },
            json={"email": regular_user["email"], "role": role["name"]}
        )

        req = requests.post(
            f"{address_api}/roles/user_roles",
            headers={
                content_type: application_json,
                "Authorization": f"Bearer {access_token_admin_user}"
            },
            json={"email": regular_user["email"]}
        )
        assert req.status_code == HTTPStatus.OK, req.text
        assert role["name"] in str(req.json()), req.text
    req = requests.post(
        f"{address_api}/roles/user_roles",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"]}
    )
    assert len(req.json()) == 5, req.text


@pytest.mark.parametrize(
    "url, method",
    (
        ("/roles/all", "GET"),
        ("/roles/user_roles", "POST"),
        ("/roles/set_role", "PATCH"),
        ("/roles/remove_role", "PATCH"),
        ("/roles/update", "PATCH"),
        ("/roles/create", "POST"),
        ("/roles/delete", "DELETE")
    )
)
def test_regular_user_cannot_access_to_roles(
    access_token_regular_user: str, url: str, method: str, regular_user: dict
) -> None:
    """Test that regular user cannot work with roles.

    Check that regular user cannot work with roles.

    Args:
        access_token_admin_user (str): Access token of admin user.
        url (str): Part of URL to check.
        method (str): HTTP method to check.
        regular_user (dict): Prepared regular user from the db.
    Returns:
        None
    """
    req = requests.request(
        url=f"{address_api}{url}",
        method=method,
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_regular_user}"
        },
        json={
            "role": "test role",
            "email": regular_user["email"],
            "new_role": "new role name"
        }
    )
    assert req.status_code == HTTPStatus.UNAUTHORIZED, req.text


def test_cascade_role_deleting(
    access_token_admin_user: str,
    regular_user: dict,
    test_5_roles: None
) -> None:
    """Test POST /roles/delete.

    Check that admin can delete assigned role.

    Args:
        access_token_admin_user (str): Access token of admin user.
        regular_user (dict): Prepared regular user from the db.
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
    Returns:
        None
    """
    # get all roles
    req = requests.get(
        f"{address_api}/roles/all",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        }
    )
    role: dict = req.json()[0]
    # assign a role
    req = requests.patch(
        f"{address_api}/roles/set_role",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"], "role": role["name"]}
    )
    assert req.status_code == HTTPStatus.OK, req.text
    # check that the role was assigned
    req = requests.post(
        f"{address_api}/roles/user_roles",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"]}
    )
    assert req.status_code == HTTPStatus.OK, req.text
    assert role["name"] in str(req.json()), req.text
    # delete the role
    req = requests.delete(
        f"{address_api}/roles/delete",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"name": role["name"]}
    )
    assert req.status_code == HTTPStatus.OK, req.text
    # check that the regular user has no the role
    req = requests.post(
        f"{address_api}/roles/user_roles",
        headers={
            content_type: application_json,
            "Authorization": f"Bearer {access_token_admin_user}"
        },
        json={"email": regular_user["email"]}
    )
    assert req.status_code == HTTPStatus.OK, req.text
    assert role["name"] not in str(req.json()), req.text
