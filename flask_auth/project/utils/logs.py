import logging

import flask


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = flask.request.headers.get('X-Request-Id')
        return True


def set_logs(app: flask.Flask):
    app.logger = logging.getLogger(__name__)
    app.logger.setLevel(logging.INFO)
    app.logger.addFilter(RequestIdFilter())
