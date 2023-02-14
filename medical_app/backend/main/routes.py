from typing import List, Tuple

from flask import Response, abort, current_app, jsonify, request

from medical_app.backend.main import bp
from medical_app.backend.main.api_helper_functions import paginate
from medical_app.backend.models import Medical, Patient


@bp.route("/medics", methods=["GET"])
def get_medics() -> Response:
    offset = request.args.get("offset", 0, type=int)
    limit = request.args.get("limit", 10, type=int)

    medics: List[Medical] = Medical.query.all()
    return jsonify(
        {
            "status": "success",
            "data": paginate(
                [medic.format_for_json() for medic in medics],
                offset=offset,
                limit=limit,
            ),
        }
    )


@bp.route("/medics", methods=["POST"])
def create_new_medic() -> Tuple[Response, int]:
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
            return jsonify({"status": "success", "data": medic_dict}), 201


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


@bp.route("/medics/<int:medic_id>/patients", methods=["GET"])
def get_patients_of_specific_medic(medic_id: int) -> Response:
    offset = request.args.get("offset", 0, type=int)
    limit = request.args.get("limit", 10, type=int)

    medic: Medical = Medical.query.get(medic_id)
    if not medic:
        abort(404)
    else:
        response_data = paginate(
            [patient.format_for_json() for patient in medic.patients],
            offset=offset,
            limit=limit,
        )
        return jsonify(
            {
                "status": "success",
                "data": response_data,
            }
        )


@bp.route("/patients", methods=["POST"])
def create() -> Tuple[Response, int]:
    with current_app.app_context():
        try:
            patient = Patient(
                first_name=request.json["firstName"],
                last_name=request.json["lastName"],
                email=request.json["email"],
                medicals=request.json["medicals"],
            )
        except KeyError:
            abort(422)
        else:
            patient_dict = patient.insert()
            return jsonify({"status": "success", "data": patient_dict}), 201


@bp.route("/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id: int) -> Response:
    patient: Patient = Patient.query.get(patient_id)
    if not patient:
        abort(404)
    else:
        return jsonify({"status": "success", "data": patient.format_for_json()})


@bp.route("/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id) -> Response:
    patient: Patient = Patient.query.get(patient_id)
    if not patient:
        abort(404)
    else:
        patient_id = patient.id
        patient.delete()
        return jsonify(
            {
                "status": "success",
                "data": patient_id,
            }
        )


@bp.route("/patients/<int:patient_id>/records", methods=["GET"])
def get_records_of_one_patient(patient_id):
    offset = request.args.get("offset", 0, type=int)
    limit = request.args.get("limit", 10, type=int)

    patient: Patient = Patient.query.get(patient_id)
    if not patient:
        abort(404)
    else:
        return jsonify(
            {
                "status": "success",
                "data": paginate(
                    [record.format_for_json() for record in patient.records],
                    limit=limit,
                    offset=offset,
                ),
            }
        )
