"""Tests of role CRUD module."""

from http import HTTPStatus

import requests  # type: ignore

from ..settings import test_settings


address_api: str = test_settings.api_address

content_type: str = "Content-Type"
application_json: str = "application/json"
headers: dict = {content_type: application_json}


def test_role_crud(test_5_roles: None, access_token_admin_user: str) -> None:
    """Test role crud.

    Test case:
        check that there are 5 prepared roles only
        create new role
        check that new role is presented in the role list
        try to create new role with name of existing role
        try to update role with wrong name
        update name of the role
        delete the role

    Args:
        test_5_roles (None): pytest fixture to prepare 5 role in the db.
        access_token_admin_user (str): Access token of admin user.
    Returns:
        None
    """
    headers["Authorization"] = f"Bearer {access_token_admin_user}"

    # check that there are 5 prepared roles
    req = requests.get(
        f"{address_api}/roles/all",
        headers=headers
    )
    assert req.status_code == HTTPStatus.OK
    assert len(req.json()) == 5

    # create new role
    req = requests.post(
        f"{address_api}/roles/create",
        headers=headers,
        json={"name": "new test role"}
    )
    assert req.status_code == HTTPStatus.OK

    # check that the role is presented.
    req = requests.get(
        f"{address_api}/roles/all",
        headers=headers
    )
    assert len(req.json()) == 6
    assert req.json()[5]["name"] == "new test role"

    # try to create role with the same name
    req = requests.post(
        f"{address_api}/roles/create",
        headers=headers,
        json={"name": "new test role"}
    )
    assert req.status_code == HTTPStatus.CONFLICT, req.text

    # try to update wrong role
    req = requests.patch(
        f"{address_api}/roles/update",
        headers=headers,
        json={"name": "555", "new_name": "new role name"}
    )
    assert req.status_code == HTTPStatus.NOT_FOUND, req.text

    # update role
    req = requests.patch(
        f"{address_api}/roles/update",
        headers=headers,
        json={"name": "new test role", "new_name": "new role name"}
    )
    assert req.status_code == HTTPStatus.OK
    req = requests.get(
        f"{address_api}/roles/all",
        headers=headers
    )
    assert len(req.json()) == 6
    assert req.json()[5]["name"] == "new role name"

    # try to delete wrong role
    req = requests.delete(
        f"{address_api}/roles/delete",
        headers=headers,
        json={"name": "555", "new_name": "new role name"}
    )
    assert req.status_code == HTTPStatus.NOT_FOUND, req.text

    # delete role
    req = requests.delete(
        f"{address_api}/roles/delete",
        headers=headers,
        json={"name": "new role name"}
    )
    assert req.status_code == HTTPStatus.OK
    req = requests.get(
        f"{address_api}/roles/all",
        headers=headers
    )
    assert len(req.json()) == 5
