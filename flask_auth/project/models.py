"""Models for auth flask app."""

import uuid
from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from flask_login import UserMixin

from flask_auth.project.db import db

# For association tables,
# the best practice is to use a table instead of a db model.
user_role = db.Table(
    "user_role",
    db.Column(
        "user_id", db.UUID, db.ForeignKey("user.id", ondelete="CASCADE")
    ),
    db.Column(
        "role_id", db.UUID, db.ForeignKey("role.id", ondelete="CASCADE")
    )
)


class LogHistory(db.Model):
    __tablename__ = "log_history"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    log_time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))


@dataclass()
class Role(db.Model):

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    name = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )

    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    is_admin = db.Column(db.Boolean)
    log_history = db.relationship('LogHistory')

    roles = db.relationship(
        "Role",
        secondary=user_role,
        backref="users",
        cascade="delete"
    )

    def __repr__(self):
        return f"<User {self.name}>"
