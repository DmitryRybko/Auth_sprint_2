"""CLI module."""

import datetime

import click
from getpass import getpass
from werkzeug.security import generate_password_hash

from flask import Blueprint

from flask_auth.project.db import db
from flask_auth.project.models import User
from flask_auth.project.utils import create_log_history_partitions

cli_blueprint = Blueprint("cli", __name__)


@cli_blueprint.cli.command("add_admin")
@click.option("--email", default="")
@click.option("--password", default="")
def create_admin(email: str = '', password: str = ''):
    if not email:
        email = input("User email: ")
    user = User.query.filter_by(email=email).first()

    if user:
        print("Email address already exists! Exit.")
        return

    if not password:
        password = getpass("Enter password: ")
        password2 = getpass("Enter password again: ")

        if password != password2:
            print("Entered passwords is different! Exit.")
            return

    new_user = User(
        email=email,
        name=email,
        password=generate_password_hash(password, method="sha256"),
        is_admin=True
    )

    db.session.add(new_user)
    db.session.commit()


@cli_blueprint.cli.command("create_partitions")
@click.option("--year", default=datetime.datetime.now().strftime("%Y"))
def create_partitions(year: str):
    create_log_history_partitions.create_log_history_partitions(year)
