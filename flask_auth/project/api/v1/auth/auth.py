from datetime import timedelta
from functools import wraps

from flask import Blueprint, request, flash, jsonify, session, render_template, url_for, redirect

from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, current_user, get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import verify_jwt_in_request

from http import HTTPStatus

from flasgger import swag_from

from flask_auth.project.db import db
from flask_auth.project.models import User
from flask_auth.project.models import LogHistory
from flask_auth.project.jwt_token_db import jwt_redis_blocklist
from flask_auth.project.app import oauth


ACCESS_EXPIRES = timedelta(hours=1)

auth_blueprint = Blueprint("auth", __name__)


def admin_access():
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            verify_jwt_in_request()
            if not current_user.is_admin:
                return jsonify({"msg": "only for admins"}), HTTPStatus.UNAUTHORIZED
            return f(*args, **kwargs)
        return decorator_function
    return decorator


@auth_blueprint.route('/')
def homepage():
    user = session.get('user')
    return render_template('auth/home.html')


@auth_blueprint.route('/login_social')
def login_social():
    redirect_uri = url_for('auth.auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_blueprint.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    userinfo = token['userinfo']
    return userinfo


@auth_blueprint.route('/logout_social')
def logout_social():
    session.pop('user', None)
    return redirect('/')


@auth_blueprint.route("/register", methods=["POST"])
@swag_from('auth_register.yaml')
def signup_post():
    email = request.json.get("email")
    name = request.json.get("name")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({"msg": "need to provide both email and password"}), HTTPStatus.BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if user:
        flash("Email address already exists")
        return jsonify({"msg": "User already exists"}), HTTPStatus.CONFLICT

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"ok": True, "message": "User created successfully!"}), HTTPStatus.OK


@auth_blueprint.route("/login", methods=["POST"])
@swag_from('auth_login.yaml')
def login_post():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), HTTPStatus.UNAUTHORIZED

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    user = User.query.filter_by(email=email).first()
    log_record = LogHistory(user_id=user.id)
    db.session.add(log_record)
    db.session.commit()

    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth_blueprint.route("/profile", methods=["GET"])
@jwt_required()
@swag_from('auth_profile_get.yaml')
def profile():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        log_history=[item.log_time for item in current_user.log_history]
    )


@auth_blueprint.route("/profile", methods=["PATCH"])
@jwt_required()
@swag_from('auth_profile_patch.yaml')
def profile_change():
    name = request.json.get("name", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=current_user.email).first()

    if name:
        user.name = name
    if password:
        user.password = generate_password_hash(password, method='sha256')
    db.session.commit()

    return jsonify({"ok": True, "message": "record updated"}), HTTPStatus.OK


# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return jsonify(access_token=access_token)


@auth_blueprint.route("/logout", methods=["POST"])
@jwt_required()
@swag_from('auth_profile_logout.yaml')
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(msg="Access token revoked")


@auth_blueprint.route("/set_admin", methods=["PATCH"])
@admin_access()
@swag_from('auth_set_admin.yaml')
def set_admin():
    user_email = request.json.get('email', None)
    is_admin = request.json.get('is_admin', None)
    user = User.query.filter_by(email=user_email).first()

    if is_admin == "True":
        user.is_admin = True
    else:
        user.is_admin = False
    db.session.commit()

    return jsonify({"ok": True, "message": "record updated"}), HTTPStatus.OK


@auth_blueprint.route("/check_token", methods=["GET"])
@jwt_required()
def check_token():
    return {"active": True}
