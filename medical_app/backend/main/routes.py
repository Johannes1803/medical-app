from flask import abort, jsonify, Response

from medical_app.backend.main import bp
from medical_app.backend.models import Medical, Patient, User


@bp.route("/", methods=["GET"])
def index() -> str:
    return "Hello world!"


@bp.route("/medics/<int:medic_id>", methods=["GET"])
def get_medic(medic_id) -> Response:
    medic: Medical = Medical.query.get(medic_id)
    if not medic:
        abort(404)
    else:
        return jsonify(medic.format_for_json())
