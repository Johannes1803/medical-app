from medical_app.backend.main import bp
from medical_app.backend.models import Patient, User


@bp.route("/", methods=["GET"])
def index() -> str:
    return "Hello world!"
