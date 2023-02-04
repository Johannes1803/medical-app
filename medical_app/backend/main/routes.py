from medical_app.backend.main import bp


@bp.route("/", methods=["GET"])
def index() -> str:
    return "Hello world!"
