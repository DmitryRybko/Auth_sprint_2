"""App module."""

from datetime import timedelta
from authlib.integrations.flask_client import OAuth


from flask import Flask
from flasgger import Swagger

from flask_migrate import Migrate

from flask_auth.project.db import db, init_db
from flask_auth.project.settings import app_settings

# Import models to create in the db.
from flask_auth.project.models import Role, User  # noqa: F401


app = Flask(__name__)
swagger = Swagger(app)


app.config["SECRET_KEY"] = app_settings.SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["DEBUG"] = int(app_settings.debug)
app.config["GOOGLE_CLIENT_ID"] = app_settings.GOOGLE_CLIENT_ID
app.config["GOOGLE_CLIENT_SECRET"] = app_settings.GOOGLE_CLIENT_SECRET

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


init_db(app)
app.app_context().push()
migrate = Migrate(app, db)


def register_blueprints():
    # register blueprints
    from flask_auth.project.api.v1.auth.auth import auth_blueprint  # noqa: E402, I202
    app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")
    from flask_auth.project.api.v1.roles.roles import roles_blueprint  # noqa: E402, I202
    app.register_blueprint(roles_blueprint, url_prefix="/api/v1/roles")
    from flask_auth.project.cli.cli import cli_blueprint  # noqa: E402, I202
    app.register_blueprint(cli_blueprint, cli_group=None)


if __name__ == "__main__":
    register_blueprints()
    app.run()
