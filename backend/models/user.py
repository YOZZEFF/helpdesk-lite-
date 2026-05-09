from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class User(db.Model):
    __tablename__ = "users"

    id: int
    email: str
    name: str
    role: str
    manager_id: int | None

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    manager = db.relationship("User", remote_side=[id], backref="subordinates")
