import os
import pathlib
from abc import ABC

import requests
from dotenv import load_dotenv

basedir: pathlib.Path = pathlib.Path(__file__).parent.resolve()


class Config:
    # db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # auth
    AUTH0_DOMAIN = "medical-app.eu.auth0.com"
    ALGORITHMS = ["RS256"]
    API_AUDIENCE = "patients-medics-info-api"


load_dotenv(basedir / ".env_test")


class TestConfig(ABC, Config):
    TESTING = True
    # db
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    APP_SECRET_KEY = "123"

    def get_access_token(
        self,
    ):
        url = f"https://{self.AUTH0_DOMAIN}/oauth/token"
        payload = {
            "client_id": self.AUTH0_CLIENT_ID,
            "client_secret": self.AUTH0_CLIENT_SECRET,
            "audience": self.API_AUDIENCE,
            "grant_type": "client_credentials",
        }

        headers = {"content-type": "application/json"}

        res = requests.post(url, json=payload, headers=headers)
        return res.json()["access_token"]


class TestConfigMedicRole(TestConfig):
    AUTH0_CLIENT_ID = os.environ.get("CLIENT_ID_MEDIC_ROLE")
    AUTH0_CLIENT_SECRET = os.environ.get("CLIENT_SECRET_MEDIC_ROLE")


class TestConfigPatientRole(TestConfig):
    AUTH0_CLIENT_ID = os.environ.get("CLIENT_ID_PATIENT_ROLE")
    AUTH0_CLIENT_SECRET = os.environ.get("CLIENT_SECRET_PATIENT_ROLE")


load_dotenv(basedir / ".env")


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "").replace(
        "postgres://", "postgresql://"
    )
    APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY")
    AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
