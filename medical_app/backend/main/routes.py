from typing import List

from flask import Response, abort, current_app, jsonify, request

from medical_app.backend.main import bp
from medical_app.backend.models import Medical, Patient


@bp.route("/medics", methods=["GET"])
def get_medics() -> Response:
    medics: List[Medical] = Medical.query.all()
    return jsonify(
        {
            "status": "success",
            "data": [medic.format_for_json() for medic in medics],
        }
    )


@bp.route("/medics", methods=["POST"])
def create_new_medic() -> Response:
    with current_app.app_context():
        try:
            medic = Medical(
                first_name=request.json["firstName"],
                last_name=request.json["lastName"],
                email=request.json["email"],
                patients=request.json["patients"],
            )
        except KeyError:
            abort(422)
        else:
            medic_dict = medic.insert()
            return jsonify({"status": "success", "data": medic_dict})


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


@bp.route("/medics/<int:medic_id>", methods=["DELETE"])
def delete_medic(medic_id) -> Response:
    medic: Medical = Medical.query.get(medic_id)
    if not medic:
        abort(404)
    else:
        medic_id = medic.id
        medic.delete()
        return jsonify(
            {
                "status": "success",
                "data": medic_id,
            }
        )
