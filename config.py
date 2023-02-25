import os
import pathlib

from dotenv import load_dotenv

basedir: pathlib.Path = pathlib.Path(__file__).parent.resolve()
load_dotenv(basedir / ".env")


class Config(object):
    # db
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace(
        "postgres://", "postgresql://"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # auth
    AUTH0_DOMAIN = "medical-app.eu.auth0.com"
    ALGORITHMS = ["RS256"]
    API_AUDIENCE = "patients-medics-info-api"

    APP_SECRET_KEY = os.environ["APP_SECRET_KEY"]
    AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
    AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
    AUTH0_AUDIENCE = os.environ["AUTH0_AUDIENCE"]
