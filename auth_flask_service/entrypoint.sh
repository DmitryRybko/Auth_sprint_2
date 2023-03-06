#!/usr/bin/env bash

# wait database and redis
python3 "$PROJECT_DIR/flask_auth/utils/wait_db.py";
python3 "$PROJECT_DIR/flask_auth/utils/wait_redis.py";

# run migrations
cd "$PROJECT_DIR/flask_auth/project";
python3 -m flask db upgrade;

# create admin user
python3 -m flask add_admin --email $ADMIN_EMAIL --password $ADMIN_PASSWORD;

# run flask_auth app with gunicorn
cd "$PROJECT_DIR/flask_auth/";
gunicorn project.wsgi_app:app -w 4 -b :$AUTH_APP_PORT;