from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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

    return app
