from __future__ import annotations

from typing import Any, Dict, List


from sqlalchemy.orm import Mapped, mapped_column

from medical_app.backend import db


def prune_keys_with_none_value(input_dict: dict) -> dict:
    """Remove keys if value is None

    :param input_dict: _description_
    :return: _description_
    """
    return {k: v for k, v in input_dict.items() if v is not None}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)

    def _to_dict(self) -> Dict[str, Any]:
        """Return dict representation of user.

        :param medicals_long_form: whether to include medical as long format, defaults to True. Set to false to avoid recursion.
        :return: dict representation of class
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
        }


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
    records: Mapped[List[Record]] = db.relationship()

    __mapper_args__ = {
        "polymorphic_identity": "patient",
    }

    def _to_dict(self) -> Dict[str, Any]:
        """Return dict representation of patient.

        :return: dict representation of classs
        """
        format_dict = super()._to_dict()
        format_dict["records"] = (
            [record.format_for_json() for record in self.records],
        )
        return format_dict

    def format_for_json(self, include_medicals_long: bool = True) -> Dict[str, Any]:
        """Return dict that can easily be jsonified.

        :param include_medicals_long: Whether to include detailed representation of medicals, defaults to True
        :return: dict representation of class to be jsonified
        """
        format_dict = self._to_dict()
        if include_medicals_long:
            format_dict["medicals"] = [
                medic.format(include_patients_long=False) for medic in self.medicals
            ]
        else:
            format_dict["medicals"] = [medic.id for medic in self.medicals]
        return prune_keys_with_none_value(format_dict)


class Medical(User):
    __tablename__ = "medical"
    id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), primary_key=True)
    patients: db.Mapped[List[Patient]] = db.relationship(
        secondary=association_table, back_populates="medicals"
    )

    __mapper_args__ = {
        "polymorphic_identity": "medical",
    }

    def format_for_json(self, include_patients_long: bool = True) -> Dict[str, Any]:
        """Return dict that can easily be jsonified.

        :param include_medicals_long: Whether to include detailed representation of medicals, defaults to True
        :return: dict representation of class to be jsonified
        """
        format_dict = self._to_dict()
        if include_patients_long:
            format_dict["patients"] = [
                patient.format_for_json(include_medicals_long=False)
                for patient in self.patients
            ]
        else:
            format_dict["patients"] = [patient.id for patient in self.patients]
        return prune_keys_with_none_value(format_dict)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String, nullable=False)
    # symptoms = db.Column(db.ARRAY(db.String))
    date_diagnosis = db.Column(db.DateTime, nullable=False)
    date_symptom_onset = db.Column(db.DateTime, nullable=False)
    date_symptom_offset = db.Column(db.DateTime, nullable=True)
    patient_id: Mapped[int] = mapped_column(db.ForeignKey("patient.id"))

    def format_for_json(self) -> Dict[str, Any]:
        """Return dict that can easily be jsonified.

        :return: dict representation of record to be jsonified
        """
        format_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "date_diagnosis": self.date_diagnosis,
            "date_symptom_onset": self.date_symptom_onset,
            "date_symptom_offest": self.date_symptom_offset,
        }
        return prune_keys_with_none_value(format_dict)
