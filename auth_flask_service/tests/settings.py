"""Test settings."""

import os

from pydantic import BaseSettings


class TestSettings(BaseSettings):
    """Test settings class."""

    auth_app_address: str = os.environ.get("AUTH_APP_ADDRESS", "localhost")
    auth_app_port: str = os.environ.get("AUTH_APP_PORT", "5000")
    api_address: str = f'http://{auth_app_address}:{auth_app_port}/api/v1'


test_settings = TestSettings()
