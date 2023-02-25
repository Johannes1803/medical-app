from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from medical_app.backend.main import bp as main_bp

    app.register_blueprint(main_bp)

    from medical_app.backend.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from medical_app.backend.authentication import bp as auth_bp

    oauth = OAuth(app)

    app.secret_key = app.config["APP_SECRET_KEY"]
    oauth.register(
        "auth0",
        client_id=app.config["AUTH0_CLIENT_ID"],
        client_secret=app.config["AUTH0_CLIENT_SECRET"],
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration',
    )
    app.oauth = oauth
    app.register_blueprint(
        auth_bp,
    )

    # Check if the database needs to be initialized
    engine = sa.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    inspector = sa.inspect(engine)
    if not inspector.has_table("medic"):
        with app.app_context():
            db.drop_all()
            db.create_all()
            app.logger.info("Initialized the database!")
    else:
        app.logger.info("Database already contains the required tables.")
    return app
