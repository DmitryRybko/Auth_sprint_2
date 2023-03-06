from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_auth.project.settings import app_settings

db = SQLAlchemy()


def init_db(app: Flask):
    pg_url: str = (
        f'postgresql://{app_settings.postgres_user}:'
        f'{app_settings.postgres_password}@{app_settings.postgres_host}'
        f':{app_settings.postgres_port}/{app_settings.postgres_db}'

    )
    app.config['SQLALCHEMY_DATABASE_URI'] = pg_url
    db.init_app(app)
