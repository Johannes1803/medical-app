import pathlib

from dotenv import load_dotenv

basedir: pathlib.Path = pathlib.Path(__file__).parent.resolve()
load_dotenv(basedir / ".env")


class Config(object):
    # db
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(basedir / "medical_app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # auth
    AUTH0_DOMAIN = "medical-app.eu.auth0.com"
    ALGORITHMS = ["RS256"]
    API_AUDIENCE = "patients-medics-info-api"
