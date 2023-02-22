import datetime
import os

import pytest
import requests
from dotenv import load_dotenv

from config import Config, basedir
from medical_app.backend import create_app, db
from medical_app.backend.models import Medical, Patient, Record


class TestFlaskConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class TestFlaskConfigAccessToken(TestFlaskConfig):
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(
        self,
    ):
        url = f"https://{self.AUTH0_DOMAIN}/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.API_AUDIENCE,
            "grant_type": "client_credentials",
        }

        headers = {"content-type": "application/json"}

        res = requests.post(url, json=payload, headers=headers)
        return res.json()["access_token"]


load_dotenv(basedir / ".env")


@pytest.fixture()
def test_config():
    return TestFlaskConfig()


@pytest.fixture()
def access_token_patient_role():
    client_id = os.environ["CLIENT_ID_PATIENT_ROLE"]
    client_secret = os.environ["CLIENT_SECRET_PATIENT_ROLE"]
    config_with_access_token = TestFlaskConfigAccessToken(
        client_id=client_id, client_secret=client_secret
    )
    return config_with_access_token.get_access_token()


@pytest.fixture()
def access_token_medic_role():
    client_id = os.environ["CLIENT_ID_MEDIC_ROLE"]
    client_secret = os.environ["CLIENT_SECRET_MEDIC_ROLE"]
    config_with_access_token = TestFlaskConfigAccessToken(
        client_id=client_id, client_secret=client_secret
    )
    return config_with_access_token.get_access_token()


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

    med_2 = Medical(
        first_name="Carla", last_name="Health", email="carla.health@mail.com"
    )
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

    patient_1.medicals += [med_1, med_2]
    patient_2.medicals.append(med_1)
    patient_3.medicals.append(med_2)

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
