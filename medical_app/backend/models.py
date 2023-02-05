from __future__ import annotations

from typing import List

from sqlalchemy.orm import Mapped, mapped_column

from medical_app.backend import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)


association_table = db.Table(
    "association_table",
    db.Column("patient_id", db.ForeignKey("patient.id"), primary_key=True),
    db.Column("medical_id", db.ForeignKey("medical.id"), primary_key=True),
)


class Patient(User):
    __tablename__ = "patient"
    id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), primary_key=True)
    medicals: Mapped[List[Medical]] = db.relationship(
        secondary=association_table, back_populates="patients"
    )

    __mapper_args__ = {
        "polymorphic_identity": "patient",
    }


class Medical(User):
    __tablename__ = "medical"
    id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), primary_key=True)
    patients: db.Mapped[List[Patient]] = db.relationship(
        secondary=association_table, back_populates="medicals"
    )

    __mapper_args__ = {
        "polymorphic_identity": "medical",
    }
