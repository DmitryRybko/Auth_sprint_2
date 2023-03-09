"""flask_auth/pywsgi.py"""

from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer  # noqa: 402

from .app import app  # noqa: 402

from .settings import app_settings


http_server = WSGIServer(('', int(app_settings.auth_app_port)), app)
http_server.serve_forever()
