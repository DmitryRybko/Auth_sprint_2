from authlib.integrations.flask_client import OAuth
from flask import current_app
from flask_auth.project.settings import app_settings


google_conf_url = app_settings.GOOGLE_CONF_URL

oauth = OAuth(current_app)
oauth.register(
    name='google',
    server_metadata_url=google_conf_url,
    client_kwargs={
        'scope': 'openid email profile'
    }
)