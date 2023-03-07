"""Flask models tests."""

import pytest

from flask_auth.project.models import User, Role


@pytest.mark.parametrize(
    "user_name, user_email, user_password",
    (
        ("test", "test@test.local", "test_password"),
    )
)
def test_new_user(user_name, user_email, user_password):
    """Test User model."""
    user = User(email=user_email, password=user_password, name=user_name)
    assert user.name == user_name
    assert user.email == user_email
    assert user.password == user_password


@pytest.mark.parametrize(
    "user_name, user_email, user_password",
    (
        ("test", "test@test.local", "test_password"),
    )
)
def test_user_repr(user_name: str, user_email: str, user_password: str):
    """Test repr function of User model."""
    user = User(email=user_email, password=user_password, name=user_name)
    assert user.__repr__() == f"<User {user_name}>"


@pytest.mark.parametrize("role_name", ("111", "new role", "a"*1024))
def test_new_role(role_name):
    """Test Role model."""
    role = Role(name=role_name)
    assert role.name == role_name


@pytest.mark.parametrize("role_name", ("111", "new role", "a"*1024))
def test_role_repr(role_name):
    """Test repr function of Role model."""
    role = Role(name=role_name)
    assert role.__repr__() == f"<Role {role_name}>"
