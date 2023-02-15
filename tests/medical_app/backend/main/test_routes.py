import flask

from medical_app.backend.models import Medical, Patient, Record


def assert_success_response_structure(res, expected_status_code: int = 200) -> None:
    """Validate success response structure.

    :param res: flask response object
    """
    assert res.status_code == expected_status_code
    assert res.json["status"] == "success"
    assert res.json["data"]


def assert_error_response_structure(res) -> None:
    """Validate error response structure.

    :param res: flask response object
    """
    assert res.status_code >= 300
    assert res.json["status"] == "error"
    assert res.json["message"]
    assert res.json["code"]

    assert res.status_code == res.json["code"]


def test_get_medics_should_return_medics_array(app):
    """Test get medics returns array of medics.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics?limit=2&offset=1")

    assert_success_response_structure(res)

    assert len(res.json["data"]) > 0


def test_post_medic_should_create_new_medic(app):
    """Test post medic creates new medic.

    :param app: flask app instance
    """
    # count medics before creating a new one
    medics = Medical.query.all()
    n_medics_before = len(medics)

    # create new medic
    res = app.test_client().post(
        "/medics",
        json={
            "firstName": "Marc",
            "lastName": "Tester",
            "email": "marc.tester@gmail.com",
            "patients": [],
        },
    )

    # test response boilerplate
    assert_success_response_structure(res, expected_status_code=201)

    # assert the id of the newly created medic is returned
    new_medic_id = res.json["data"].get("id")
    assert new_medic_id

    # check new medic is in db
    assert Medical.query.get(new_medic_id)

    # check medics count increased by one
    medics = Medical.query.all()
    n_medics_after = len(medics)
    assert n_medics_before + 1 == n_medics_after


def test_post_medic_missing_attribute_should_raise_422(app):
    """Test post medic with missing attribute raises 422 error.

    :param app: flask app instance
    """
    res = app.test_client().post(
        "/medics",
        json={
            "firstName": "Marc",
            "email": "marc.tester@gmail.com",
            "patients": [],
        },
    )

    assert_error_response_structure(res)

    assert res.json["code"] == 422


def test_get_medic_should_return_medic(app) -> None:
    """Test get medic returns medic.

    :param app: flask app instance
    """
    # ToDo: Link medic id to test setup
    res: flask.Response = app.test_client().get("/medics/1")

    assert_success_response_structure(res)


def test_get_medic_non_existing_should_return_404(app) -> None:
    """Test get medic with non-existing id raises 404 error.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics/1000000")

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_delete_medic_should_remove_medic_from_db(app):
    """Test delete medic removes medic from db.

    This includes removing the medic from the list of medics of each patient.

    :param app: flask app instance
    """
    # get patient ids associated with medic before deletion
    medic = Medical.query.get(1)
    patient_ids = [patient.id for patient in medic.patients]

    res: flask.Response = app.test_client().delete("/medics/1")

    assert_success_response_structure(res)

    # assert medic is no longer in db
    assert Medical.query.get(1) is None

    # test response contains medic id
    assert res.json["data"] == 1

    # test no former patient still has medic in his list of medics
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    for patient in patients:
        assert medic not in patient.medicals


def test_delete_medic_non_existing_should_return_404(app) -> None:
    """Test trying to delete a non existing medic raises 404.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().delete("/medics/1000000")

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_get_patients_of_medic(app) -> None:
    """Test get patients of medic returns array of patients.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics/2/patients?limit=100")

    assert_success_response_structure(res)

    # we know that medic one has a patient
    assert len(res.json["data"]) > 0


def test_get_patients_of_medic_non_existing_should_return_404(app) -> None:
    """Test get medic with non-existing id raises 404 error.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics/1000000/patients")

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_get_patient_should_return_patient(app):
    """Test get patient returns patient.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/patients/5")

    assert_success_response_structure(res)


def test_get_patient_non_existing_should_return_404(app):
    """Test get patient returns patient.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/patients/50")

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_post_patient_should_create_new_patient(app):
    """Test post patient returns patient.

    :param app: flask app instance
    """
    # count medics before creating a new one
    patients = Patient.query.all()
    n_patients_before = len(patients)

    # create new medic
    res = app.test_client().post(
        "/patients",
        json={
            "firstName": "Anna",
            "lastName": "Patient",
            "email": "anna.patient@gmail.com",
            "medicals": [],
        },
    )

    # test response boilerplate
    assert_success_response_structure(res, expected_status_code=201)

    # assert the id of the newly created medic is returned
    new_patient_id = res.json["data"].get("id")
    assert new_patient_id

    # check new medic is in db
    assert Patient.query.get(new_patient_id)

    # check medics count increased by one
    patients = Patient.query.all()
    n_patients_after = len(patients)
    assert n_patients_before + 1 == n_patients_after


def test_post_patient_missing_attribute_should_raise_422(app):
    """Test post medic with missing attribute raises 422 error.

    :param app: flask app instance
    """
    res = app.test_client().post(
        "/patients",
        json={
            "firstName": "Marc",
            "lastName": "Tester",
            "patients": [],
        },
    )

    assert_error_response_structure(res)

    assert res.json["code"] == 422


def test_delete_patient_should_remove_patient_from_db(app):
    """Test delete patient removes patient from db.

    This includes removing the patient from the list of patients of each medic.

    :param app: flask app instance
    """
    patient_id = 5

    # get patient ids associated with medic before deletion
    patient = Patient.query.get(patient_id)
    assert patient
    medic_ids = [medic.id for medic in patient.medicals]

    res: flask.Response = app.test_client().delete(f"/patients/{patient_id}")

    assert_success_response_structure(res)

    # verify patient was deleted
    assert Patient.query.get(patient_id) is None

    # test response contains patient id
    assert res.json["data"] == patient_id

    # test no former medic still has patient in his list of patients
    medics = Medical.query.filter(Medical.id.in_(medic_ids)).all()
    for medic in medics:
        assert patient not in medic.patients


def test_delete_patient_non_existing_should_return_404(app) -> None:
    """Test trying to delete a non existing patient raises 404.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().delete("/patients/1000000")

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_get_records_of_patients_should_return_records(app) -> None:
    """Test getting records of a patient returns a list of records.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/patients/5/records")

    assert_success_response_structure(res)

    assert len(res.json["data"]) > 0


def test_get_records_of_patients_non_existing_should_raise_404(app) -> None:
    """Test trying to get records of a non-existent patient raises 404.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/patients/2/records")

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_post_new_record_should_add_record_to_patient(app) -> None:
    """Test posting a new record to patient creates record in db.

    :param app: flask app instance
    """
    # create new record
    patient_id = 5
    res = app.test_client().post(
        f"/patients/{patient_id}/records",
        json={
            "title": "back pain",
            "description": "Caused by long working hours.",
            # "symptoms": ["string"],
            "dateDiagnosis": "2023-02-14",
            "dateSymptomOnset": "2023-02-07",
            "patientId": patient_id,
        },
    )

    # test response boilerplate
    assert_success_response_structure(res, expected_status_code=201)

    # assert the id of the newly created medic is returned
    new_record_id = res.json["data"].get("id")
    assert new_record_id

    # check new medic is in db
    assert Record.query.get(new_record_id)


def test_get_record_should_return_record(app) -> None:
    """Test getting a record returns a record.

    :param app: flask app instance
    """
    patient_id = 5
    record_id = 1
    res = app.test_client().get(
        f"/patients/{patient_id}/records/{record_id}",
    )
    assert_success_response_structure(res)

    assert len(res.json["data"]) > 0


def test_get_non_existing_record_should_return_404(app) -> None:
    """Test getting a non existing record raises 404.

    :param app: flask app instance
    """
    patient_id = 5
    record_id = 10
    res = app.test_client().get(
        f"/patients/{patient_id}/records/{record_id}",
    )
    assert_error_response_structure(res)

    assert res.json["code"] == 404
