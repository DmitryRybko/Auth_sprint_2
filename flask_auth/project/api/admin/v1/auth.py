"""Api/admin/v1/auth module."""

from http import HTTPStatus
from logging import getLogger

from flask import Blueprint, jsonify, request

from flask_auth.project.models import User

from sqlalchemy.orm.exc import NoResultFound


logger = getLogger(__name__)

auth_admin_blueprint = Blueprint("auth_admin", __name__)


@auth_admin_blueprint.route("/users", methods=["GET"])
def get_all_users() -> tuple[str, HTTPStatus]:
    """Return all users with pagination."""
    page: int = request.args.get("page", default=1, type=int)
    limit: int = request.args.get("limit", default=10, type=int)

    users: list[User] = User.query.paginate(
        page=page, per_page=limit, error_out=False
    ).items

    return jsonify([user.serialize for user in users]), HTTPStatus.OK


@auth_admin_blueprint.route("/user", methods=["GET"])
def get_user_info() -> tuple[str, HTTPStatus]:
    """Return user info."""
    user_id: str = request.args.get("user_id", default="")
    user_email: str = request.args.get("user_email", default="")

    if user_id and user_email:
        return jsonify({"error": "one param only"}), HTTPStatus.BAD_REQUEST
    if not user_id and not user_email:
        return jsonify(
            {"error": "user_id and user_email not found in request"}
        ), HTTPStatus.BAD_REQUEST

    if user_id:
        try:
            user = User.query.filter(id=user_id).one()
        except NoResultFound as e:
            logger.info(e)
            return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
        return jsonify(user.serialize), HTTPStatus.OK
    else:
        try:
            user = User.query.filter(email=user_email).one()
        except NoResultFound as e:
            logger.info(e)
            return jsonify({"error": "user not found"}), HTTPStatus.NOT_FOUND
        return jsonify(user.serialize), HTTPStatus.OK
