import datetime
import os

import pytest

from config import TestConfigMedicRole, TestConfigPatientRole
from medical_app.backend import create_app, db
from medical_app.backend.models import Medic, Patient, Record

test_config_medic_role = TestConfigMedicRole()
test_config_patient_role = TestConfigPatientRole()


@pytest.fixture()
def app():
    app = create_app(test_config_medic_role)
    with app.app_context() as app_context:
        app_context.push()
        db.create_all()
        populate_test_db()

    yield app

    with app.app_context() as app_context:
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def access_token_patient_role():
    return test_config_patient_role.get_access_token()


@pytest.fixture()
def access_token_medic_role():
    return test_config_medic_role.get_access_token()


def populate_test_db():
    med_1 = Medic(first_name="John", last_name="Doc", email="john.doc@mail.com")
    db.session.add(med_1)

    med_2 = Medic(first_name="Carla", last_name="Health", email="carla.health@mail.com")
    db.session.add(med_2)

    patient_1 = Patient(
        first_name="Mister", last_name="Patient", email="patient@mail.com"
    )
    db.session.add(patient_1)

    patient_2 = Patient(
        first_name="Anthony", last_name="Smith", email="Anthony.Smith@gmx.com"
    )
    db.session.add(patient_2)

    patient_3 = Patient(
        first_name="Laura", last_name="Oneal", email="laura.oneal@mail.com"
    )
    db.session.add(patient_3)

    patient_4 = Patient(first_name="Lena", last_name="Pitt", email="Lena.pitt@mail.com")
    db.session.add(patient_4)
    db.session.commit()

    patient_1.medics += [med_1, med_2]
    patient_2.medics.append(med_1)
    patient_3.medics.append(med_2)

    record_1 = Record(
        title="Flew",
        description="influenca season",
        date_diagnosis=datetime.datetime.strptime("2022-12-01", "%Y-%m-%d"),
        date_symptom_onset=datetime.datetime.strptime("2022-11-21", "%Y-%m-%d"),
        patient_id=patient_1.id,
    )
    db.session.add(record_1)
    patient_3.records.append(record_1)
    db.session.commit()
