"""Module to push and to pop jwt tokens in redis."""

# third party imports
import redis

# flask imports
from flask import current_app
from flask_jwt_extended import JWTManager

# app imports
from flask_auth.project.models import User
from flask_auth.project.settings import app_settings

jwt = JWTManager(current_app)

jwt_redis_blocklist = redis.StrictRedis(
    host=app_settings.redis_host,
    port=int(app_settings.redis_port),
    db=0,
    decode_responses=True
)


# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    """Check that the token is in blocklist."""
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.user_identity_loader
def user_identity_lookup(user):
    """Return user."""
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    """Return user by data in token."""
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).one_or_none()
