"""flask_auth/settings.py."""

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    """Flask application settings class."""

    postgres_host: str = 'localhost'
    postgres_port: str = '54321'
    postgres_user: str = 'app'
    postgres_password: str = '123qwe'
    postgres_db: str = 'auth'

    redis_host: str = 'localhost'
    redis_port: str = '6379'

    SECRET_KEY: str = 'some_secret_string'

    auth_app_address: str = '0.0.0.0'
    auth_app_port: str = '8002'

    jaeger_host: str = 'localhost'
    jaeger_port: str = '6831'

    debug: str = '0'


app_settings = AppSettings()
