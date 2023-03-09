from datetime import timedelta
from flask import Blueprint, request, flash, jsonify
from http import HTTPStatus
from flasgger import swag_from

from flask_auth.project.db import db
from flask_auth.project.models import User, Role
from flask_auth.project.api.v1.auth.auth import admin_access

ACCESS_EXPIRES = timedelta(hours=1)

roles_blueprint = Blueprint("roles", __name__)


@roles_blueprint.route("/create", methods=["POST"])
@admin_access()
@swag_from('roles_create.yaml')
def create_role():

    name = request.json.get("name")
    role = Role.query.filter_by(name=name).first()

    if role:
        flash("Role already exists")
        return jsonify({"msg": "Role already exists"}), HTTPStatus.CONFLICT

    new_role = Role(name=name)

    db.session.add(new_role)
    db.session.commit()

    return jsonify({"ok": True, "message": "Role created successfully!"}), HTTPStatus.OK


@roles_blueprint.route("/delete", methods=['DELETE'])
@admin_access()
@swag_from('roles_delete.yaml')
def delete_role():

    name = request.json.get("name")
    role = Role.query.filter_by(name=name).first()
    if not role:
        return jsonify({"ok": True, "message": "Role does not exist"}), HTTPStatus.NOT_FOUND

    db.session.delete(role)
    db.session.commit()

    return jsonify({"ok": True, "message": "Role deleted successfully!"}), HTTPStatus.OK


@roles_blueprint.route("/update", methods=["PATCH"])
@admin_access()
@swag_from('roles_update.yaml')
def update_role():
    name = request.json.get("name")
    new_name = request.json.get("new_name")
    role = Role.query.filter_by(name=name).first()

    if role:
        role.name = new_name
    else:
        return jsonify({"ok": True, "message": "Role does not exist"}), HTTPStatus.NOT_FOUND

    db.session.commit()

    return jsonify({"ok": True, "message": "role updated"}), HTTPStatus.OK


@roles_blueprint.route("/all", methods=["GET"])
@admin_access()
@swag_from('roles_all.yaml')
def get_all_roles():
    roles = Role.query.all()
    return jsonify([{'id': r.id, 'name': r.name} for r in roles])


@roles_blueprint.route("/set_role", methods=["PATCH"])
@admin_access()
@swag_from('roles_set_role.yaml')
def set_role():
    user_email = request.json.get("email", None)
    new_role = request.json.get("role", None)
    user = User.query.filter_by(email=user_email).first()
    role = Role.query.filter_by(name=new_role).first()

    role.users.append(user)
    db.session.commit()

    return jsonify({"ok": True, "message": "record updated"}), HTTPStatus.OK


@roles_blueprint.route("/remove_role", methods=["PATCH"])
@admin_access()
@swag_from('roles_remove_role.yaml')
def remove_role():
    user_email = request.json.get("email", None)
    removed_role = request.json.get("role", None)
    user = User.query.filter_by(email=user_email).first()
    role = Role.query.filter_by(name=removed_role).first()

    role.users.remove(user)
    db.session.commit()

    return jsonify({"ok": True, "message": "role removed"}), HTTPStatus.OK


@roles_blueprint.route("/user_roles", methods=["POST"])
@admin_access()
@swag_from('roles_user.yaml')
def user_roles():
    user_email = request.json.get("email")
    user = User.query.filter_by(email=user_email).first()
    list_user_roles = user.roles

    return jsonify([{'id': r.id, 'name': r.name} for r in list_user_roles])
