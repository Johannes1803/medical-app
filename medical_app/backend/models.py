from __future__ import annotations

from typing import Any, Dict, List, Set

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medical_app.backend import db


def prune_keys_with_none_value(input_dict: dict) -> dict:
    """Remove keys if value is None

    :param input_dict: dict with potential none values
    :return: pruned dict
    """
    return {k: v for k, v in input_dict.items() if v is not None}


class User(db.Model):
    empty_string_forbidden_cols: Set = {"first_name", "last_name", "email"}
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(64), unique=True, nullable=False)

    def __init__(self, **kwargs) -> None:
        empty_string_params = {
            arg_key
            for arg_key, arg_value in kwargs.items()
            if isinstance(arg_value, str) and len(arg_value) == 0
        }
        if empty_string_violations := (
            empty_string_params & self.empty_string_forbidden_cols
        ):
            raise ValueError(
                f"Empty string as value forbidden for {empty_string_violations}"
            )
        super().__init__(**kwargs)

    def format_for_json(self, **kwargs) -> Dict[str, Any]:
        """Return dict representation of user.

        :return: dict representation of class
        """
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
        }

    def insert(self) -> Dict[str, Any]:
        """Insert user into db.

        :return: dict representation of user.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise (e)
        else:
            instance_dict_to_be_jsonified = self.format_for_json()
            return instance_dict_to_be_jsonified
        finally:
            db.session.close()

    def delete(self) -> int:
        """Delete self from db.

        :return: id of deleted user
        """
        id = self.id
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        else:
            return id
        finally:
            db.session.close()


association_table = db.Table(
    "association_table",
    Column("patient_id", ForeignKey("patient.id"), primary_key=True),
    Column("medic_id", ForeignKey("medic.id"), primary_key=True),
)


class Patient(User):
    __tablename__ = "patient"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    medics: Mapped[List[Medic]] = relationship(
        secondary=association_table, back_populates="patients"
    )
    records: Mapped[List[Record]] = relationship("Record", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "patient",
    }

    def format_for_json(self, **kwargs) -> Dict[str, Any]:
        """Return dict that can easily be jsonified.

        :param include_medics_long: Whether to include detailed representation of medics, defaults to True
        :return: dict representation of class to be jsonified
        """
        format_dict = super().format_for_json(**kwargs)
        format_dict["records"] = [record.format_for_json() for record in self.records]

        if kwargs.get("include_medics_long"):
            format_dict["medics"] = [
                medic.format_for_json(include_patients_long=False)
                for medic in self.medics
            ]
        else:
            format_dict["medics"] = [medic.id for medic in self.medics]
        return prune_keys_with_none_value(format_dict)


class Medic(User):
    __tablename__ = "medic"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    patients: Mapped[List[Patient]] = relationship(
        secondary=association_table, back_populates="medics"
    )

    __mapper_args__ = {
        "polymorphic_identity": "medic",
    }

    def format_for_json(self, **kwargs) -> Dict[str, Any]:
        """Return dict that can easily be jsonified.

        :param include_medics_long: Whether to include detailed representation of medics, defaults to True
        :return: dict representation of class to be jsonified
        """
        format_dict = super().format_for_json(**kwargs)
        if kwargs.get("include_patients_long"):
            format_dict["patients"] = [
                patient.format_for_json(include_medics_long=False)
                for patient in self.patients
            ]
        else:
            format_dict["patients"] = [patient.id for patient in self.patients]
        return prune_keys_with_none_value(format_dict)

    def add_patient(self, patient: Patient) -> Dict[str, Any]:
        """Add patient to medic.

        :param patient_id: id of patient to add
        :return: dict represenation of self to be jsonified
        """
        try:
            self.patients.append(patient)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        else:
            instance_dict_to_be_jsonified = self.format_for_json()
            return instance_dict_to_be_jsonified
        finally:
            db.session.close()

    def update(self, **kwargs) -> Dict[str, Any]:
        """Update medic with given kwargs.

        :return: dict representation of updated medic.
        """
        try:
            for attribute_name, v in kwargs.items():
                getattr(self, attribute_name)
                setattr(self, attribute_name, v)
                db.session.commit()

        except (SQLAlchemyError, AttributeError) as e:
            db.session.rollback()
            raise (e)
        else:
            instance_dict_to_be_jsonified = self.format_for_json()
            return instance_dict_to_be_jsonified
        finally:
            db.session.close()


class Record(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    description = Column(String, nullable=False)
    date_diagnosis = Column(DateTime, nullable=False)
    date_symptom_onset = Column(DateTime, nullable=False)
    date_symptom_offset = Column(DateTime, nullable=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"))

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
            "patient_id": self.patient_id,
        }
        return prune_keys_with_none_value(format_dict)

    def insert(self) -> Dict[str, Any]:
        """Insert record into db.

        :return: dict representation of record.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        else:
            instance_dict_to_be_jsonified = self.format_for_json()
            return instance_dict_to_be_jsonified
        finally:
            db.session.close()

    def delete(self) -> int:
        """Delete self from db.

        :return: id of deleted user
        """
        id = self.id
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        else:
            return id
        finally:
            db.session.close()
