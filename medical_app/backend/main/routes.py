from flask import Response, abort, jsonify

from medical_app.backend.main import bp
from medical_app.backend.models import Medical, Patient


@bp.route("/medics/<int:medic_id>", methods=["GET"])
def get_medic(medic_id) -> Response:
    medic: Medical = Medical.query.get(medic_id)
    if not medic:
        abort(404)
    else:
        return jsonify(
            {
                "status": "success",
                "data": medic.format_for_json(),
            }
        )
