import datetime

import pytest

from config import Config
from medical_app.backend import create_app, db
from medical_app.backend.models import Medical, Patient, Record


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


@pytest.fixture()
def test_config():
    return TestConfig()


@pytest.fixture()
def app(test_config: Config):
    app = create_app(test_config)
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


def populate_test_db():
    med_1 = Medical(first_name="John", last_name="Doc", email="john.doc@mail.com")
    db.session.add(med_1)

    patient = Patient(
        first_name="Mister", last_name="Patient", email="patient@mail.com"
    )
    db.session.add(patient)

    patient.medicals.append(med_1)
    db.session.commit()

    record = Record(
        title="Flew",
        description="influenca season",
        date_diagnosis=datetime.datetime.strptime("2022-12-01", "%Y-%m-%d"),
        date_symptom_onset=datetime.datetime.strptime("2022-11-21", "%Y-%m-%d"),
        patient_id=patient.id,
    )
    db.session.add(record)
    db.session.commit()
