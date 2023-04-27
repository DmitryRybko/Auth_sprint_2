"""Models for auth flask app."""

import uuid
import datetime
from dataclasses import dataclass

from sqlalchemy import func, UniqueConstraint
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

log_history_table_name: str = "log_history"


def create_partition(target, connection, **kw) -> None:
    """Create partitions for log_history table."""
    cur_year: str = datetime.datetime.now().strftime("%Y")
    for i in range(1, 12):
        connection.execute(
            (
                "CREATE TABLE IF NOT EXISTS "
                f'"{log_history_table_name}_y{cur_year}m{i}" '
                f"PARTITION OF {log_history_table_name}"
                f"FOR VALUES FROM ('{cur_year}-{i}-01') "
                f"TO ('{cur_year}-{i+1}-01');"
            )
        )
    connection.execute(
        (
            "CREATE TABLE IF NOT EXISTS "
            f'"{log_history_table_name}_y{cur_year}m12" '
            f"PARTITION OF {log_history_table_name}"
            f"FOR VALUES FROM ('{cur_year}-12-01') "
            f"TO ('{cur_year}-12-31');"
        )
    )


class LogHistory(db.Model):
    __tablename__ = log_history_table_name
    __table_args__ = (
        UniqueConstraint('id', 'log_time'),
        {
            'postgresql_partition_by': 'RANGE (log_time)',
            'listeners': [('after_create', create_partition)],
        }
    )
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

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "name": self.name,
        }


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
    log_history = db.relationship("LogHistory")

    roles = db.relationship(
        "Role",
        secondary=user_role,
        backref="users",
        cascade="delete"
    )

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "roles": [role.serialize for role in self.roles],
        }

    def __repr__(self):
        return f"<User {self.name}>"
