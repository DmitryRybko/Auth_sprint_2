"""App module."""

from datetime import timedelta
from flask import Flask, request, json
from flasgger import Swagger
from flask_migrate import Migrate
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from werkzeug.exceptions import HTTPException

from flask_auth.project.db import db, init_db
from flask_auth.project.settings import app_settings
# Import models to create in the db.
from flask_auth.project.models import Role, User  # noqa: F401
from flask_auth.project.utils.configure_tracer import configure_tracer


configure_tracer()
app = Flask(__name__)
if int(app_settings.jaeger_enabled) == 1:
    FlaskInstrumentor().instrument_app(app)
swagger = Swagger(app)


@app.before_request
def before_request():
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        raise RuntimeError("request id is required")


app.config["SECRET_KEY"] = app_settings.SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["DEBUG"] = int(app_settings.debug)

app.config["GOOGLE_CLIENT_ID"] = app_settings.GOOGLE_CLIENT_ID
app.config["GOOGLE_CLIENT_SECRET"] = app_settings.GOOGLE_CLIENT_SECRET

init_db(app)
app.app_context().push()
migrate = Migrate(app, db)


# register blueprints
from flask_auth.project.api.v1.auth.auth import auth_blueprint  # noqa: E402, I202
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")
from flask_auth.project.api.v1.roles.roles import roles_blueprint  # noqa: E402, I202
app.register_blueprint(roles_blueprint, url_prefix="/api/v1/roles")
from flask_auth.project.cli.cli import cli_blueprint  # noqa: E402, I202
app.register_blueprint(cli_blueprint, cli_group=None)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    app.run()
