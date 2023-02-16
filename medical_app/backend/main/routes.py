from datetime import datetime
from typing import List, Optional, Tuple

from flask import Response, abort, current_app, jsonify, request

from medical_app.backend.main import bp
from medical_app.backend.main.api_helper_functions import paginate
from medical_app.backend.models import Medical, Patient, Record


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
    patient_ids: List[int] = request.json.get("patient_ids", [])
    patients = []
    with current_app.app_context():
        for patient_id in patient_ids:
            patient = Patient.query.get(patient_id)
            if not patient:
                abort(422)
            else:
                patients.append(patient)

        try:
            medic = Medical(
                first_name=request.json["firstName"],
                last_name=request.json["lastName"],
                email=request.json["email"],
                patients=patients,
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
def create_new_patient() -> Tuple[Response, int]:
    medic_ids: List[int] = request.json.get("medicIds", [])
    medics = []
    with current_app.app_context():
        for medic_id in medic_ids:
            medic = Medical.query.get(medic_id)
            if not medic:
                abort(422)
            else:
                medics.append(medic)
        try:
            medic = Patient(
                first_name=request.json["firstName"],
                last_name=request.json["lastName"],
                email=request.json["email"],
                medicals=medics,
            )
        except KeyError:
            abort(422)
        else:
            patient_dict = medic.insert()
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
        patient_id = patient.delete()
        return jsonify(
            {
                "status": "success",
                "data": patient_id,
            }
        )


@bp.route("/patients/<int:patient_id>/records", methods=["GET"])
def get_records_of_one_patient(patient_id: int) -> Response:
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


@bp.route("/patients/<int:patient_id>/records", methods=["POST"])
def add_record_to_patient(patient_id: int) -> Tuple[Response, int]:
    date_format = "%Y-%m-%d"

    patient: Optional[Patient] = Patient.query.get(patient_id)
    if not patient:
        abort(404)
    else:
        try:
            # process request body
            date_symptom_offset_str: str = request.json.get("dateSymptomOffset")
            date_symptom_offset: Optional[datetime] = (
                datetime.strptime(date_symptom_offset_str, date_format)
                if date_symptom_offset_str
                else None
            )
            date_symptom_onset: datetime = datetime.strptime(
                request.json["dateSymptomOnset"], date_format
            )
            date_diagnosis: datetime = datetime.strptime(
                request.json["dateDiagnosis"], date_format
            )
            record = Record(
                title=request.json["title"],
                description=request.json["description"],
                date_diagnosis=date_diagnosis,
                date_symptom_onset=date_symptom_onset,
                date_symptom_offset=date_symptom_offset,
                patient_id=request.json["patientId"],
            )
        except KeyError:
            # ToDo: logging in blue prints
            abort(422)
        else:
            record_dict = record.insert()
            return jsonify({"status": "success", "data": record_dict}), 201


@bp.route("/patients/<int:patient_id>/records/<int:record_id>", methods=["GET"])
def get_record(patient_id: int, record_id: int):
    """Get record of specific patient.

    :param patient_id: id of patient
    :param record_id: id of record
    """
    patient: Optional[Patient] = Patient.query.get(patient_id)
    if not patient:
        abort(404)
    else:
        matching_records: list[Record] = [
            record for record in patient.records if record.id == record_id
        ]
        if len(matching_records) == 0:
            abort(404)
        elif len(matching_records) > 1:
            abort(500)
        else:
            record = matching_records[0]
            record_dict = record.format_for_json()
            return jsonify({"status": "success", "data": record_dict})


@bp.route("/patients/<int:patient_id>/records/<int:record_id>", methods=["DELETE"])
def delete_record(patient_id: int, record_id: int) -> Response:
    """Delete record from db.

    :param patient_id: id of patient
    :param record_id: id of record
    :return: flask response
    """
    patient: Optional[Patient] = Patient.query.get(patient_id)
    if not patient:
        abort(404)
    else:
        matching_records: list[Record] = [
            record for record in patient.records if record.id == record_id
        ]
        if len(matching_records) == 0:
            abort(404)
        elif len(matching_records) > 1:
            abort(500)
        else:
            record: Record = matching_records[0]
            record_id = record.delete()
            return jsonify({"status": "success", "data": record_id})
