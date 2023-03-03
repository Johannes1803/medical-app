from typing import Optional

import flask

from medical_app.backend.models import Medic, Patient, Record, db


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
    res: flask.Response = app.test_client().get(
        "/medics?limit=2&offset=1",
    )

    assert_success_response_structure(res)

    assert len(res.json["data"]) > 0


def test_post_medic_should_create_new_medic(app, access_token_medic_role):
    """Test post medic creates new medic.

    :param app: flask app instance
    """
    # count medics before creating a new one
    medics = Medic.query.all()
    n_medics_before = len(medics)

    # create new medic
    res = app.test_client().post(
        "/medics",
        json={
            "firstName": "Franz",
            "lastName": "Hungertobel",
            "email": "franz.hungertobel@mail.com",
            "patientIds": [3, 4],
        },
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    # test response boilerplate
    assert_success_response_structure(res, expected_status_code=201)

    # assert the id of the newly created medic is returned
    new_medic_id = res.json["data"].get("id")
    assert new_medic_id

    # check new medic is in db
    new_medic: Optional[Medic] = db.session.get(Medic, new_medic_id)
    assert new_medic

    # check new medic has patients
    assert new_medic.patients
    assert new_medic.patients[0].first_name

    # check medics count increased by one
    medics = Medic.query.all()
    n_medics_after = len(medics)
    assert n_medics_before + 1 == n_medics_after


def test_post_medic_missing_attribute_should_raise_422(app, access_token_medic_role):
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
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_error_response_structure(res)

    assert res.json["code"] == 422


def test_post_medic_invalid_attribute_should_raise_422(app, access_token_medic_role):
    """Test post medic with missing attribute raises 422 error.

    :param app: flask app instance
    """
    res = app.test_client().post(
        "/medics",
        json={"email": "", "firstName": "", "id": 1, "lastName": "", "patients": []},
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_error_response_structure(res)

    assert res.json["code"] == 422


def test_get_medic_should_return_medic(app) -> None:
    """Test get medic returns medic.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics/1")

    assert_success_response_structure(res)


def test_get_medic_non_existing_should_return_404(app) -> None:
    """Test get medic with non-existing id raises 404 error.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics/1000000")

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_delete_medic_should_remove_medic_from_db(app, access_token_medic_role):
    """Test delete medic removes medic from db.

    This includes removing the medic from the list of medics of each patient.

    :param app: flask app instance
    """
    # get patient ids associated with medic before deletion
    medic_id: int = 1
    medic = db.session.get(Medic, medic_id)
    patient_ids = [patient.id for patient in medic.patients]

    res: flask.Response = app.test_client().delete(
        f"/medics/{medic_id}",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_success_response_structure(res)

    # assert medic is no longer in db
    assert db.session.get(Medic, medic_id) is None

    # test response contains medic id
    assert res.json["data"] == medic_id

    # test no former patient still has medic in his list of medics
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    for patient in patients:
        assert medic not in patient.medics


def test_delete_medic_non_existing_should_return_404(
    app, access_token_medic_role
) -> None:
    """Test trying to delete a non existing medic raises 404.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().delete(
        "/medics/1000000",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_delete_medic_not_authorized_should_return_403(
    app, access_token_patient_role
) -> None:
    """Test trying to delete a non existing medic raises 403.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().delete(
        "/medics/1",
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    assert_error_response_structure(res)
    assert res.status_code == 403


def test_patch_medic_should_modify_medic(app, access_token_medic_role) -> None:
    """Test patching a medic updates his information in the db.

    :param app: flask app instance
    """
    medic_id = 2
    new_patient_ids = [3]

    res: flask.Response = app.test_client().patch(
        f"/medics/{medic_id}",
        json={
            "email": "newMail@mail.com",
            "lastName": "JustMarried",
            "patientIds": new_patient_ids,
        },
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_success_response_structure(res)

    # test an unchanged attribute
    assert res.json["data"]["firstName"] == "Carla"
    # test a modified attribute
    assert set(res.json["data"]["patients"]) == set(new_patient_ids)


def test_patch_medic_non_existing_attribute_raises_422(
    app, access_token_medic_role
) -> None:
    """Test patching a medic with attribute not defined in model raises 422.

    :param app: flask app instance
    """
    medic_id = 1

    res: flask.Response = app.test_client().patch(
        f"/medics/{medic_id}",
        json={
            "email": "newMail@mail.com",
            "lastName": "JustMarried",
            "hobbies": "playing guitar",
        },
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_error_response_structure(res)
    assert res.json["code"] == 422


def test_get_patients_of_medic(app, access_token_medic_role) -> None:
    """Test get patients of medic returns array of patients.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get(
        "/medics/2/patients?limit=100",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_success_response_structure(res)

    # we know that medic one has a patient
    assert len(res.json["data"]) > 0


def test_get_patients_of_medic_non_existing_should_return_404(
    app, access_token_medic_role
) -> None:
    """Test get medic with non-existing id raises 404 error.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get(
        "/medics/1000000/patients",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_add_patient_to_medic(app, access_token_medic_role) -> None:
    """Test adding patient to medic updates medic patient mapping.

    :param app: flask app instance
    """
    medic_id = 1
    patient_id = 3
    res: flask.Response = app.test_client().put(
        f"/medics/{medic_id}/patients/{patient_id}",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )
    assert_success_response_structure(res)

    # test medic is added to patient
    patient = db.session.get(Patient, patient_id)
    assert [medic for medic in patient.medics if medic.id == medic_id]

    # test patient is added to medic
    medic = db.session.get(Medic, medic_id)
    assert [patient for patient in medic.patients if patient.id == patient_id]


def test_add_patient_to_medic_raises_404_if_patient_not_found(
    app, access_token_medic_role
) -> None:
    """Test adding patient to medic raises 404 if patient not in db.

    :param app: flask app instance
    """
    medic_id = 1
    patient_id = 1
    res: flask.Response = app.test_client().put(
        f"/medics/{medic_id}/patients/{patient_id}",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )
    assert_error_response_structure(res)
    assert res.json["code"] == 404


def test_get_patient_should_return_patient(app, access_token_patient_role):
    """Test get patient returns patient.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get(
        "/patients/5",
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    assert_success_response_structure(res)


def test_get_patient_non_existing_should_return_404(app, access_token_patient_role):
    """Test get patient returns patient.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get(
        "/patients/50",
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_post_patient_should_create_new_patient(app, access_token_patient_role):
    """Test post patient returns patient.

    :param app: flask app instance
    """
    # count patients before creating a new one
    patients = Patient.query.all()
    n_patients_before = len(patients)

    # create new patient
    res = app.test_client().post(
        "/patients",
        json={
            "firstName": "Anna",
            "lastName": "Patient",
            "email": "anna.patient@gmail.com",
            "medicIds": [2],
        },
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    # test response boilerplate
    assert_success_response_structure(res, expected_status_code=201)

    # assert the id of the newly created patient is returned
    new_patient_id = res.json["data"].get("id")
    assert new_patient_id

    # check new patient is in db
    new_patient = db.session.get(Patient, new_patient_id)

    # check new patient has medic added
    assert new_patient.medics[0].email

    # check medics count increased by one
    patients = Patient.query.all()
    n_patients_after = len(patients)
    assert n_patients_before + 1 == n_patients_after


def test_post_patient_missing_attribute_should_raise_422(
    app, access_token_patient_role
):
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
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    assert_error_response_structure(res)

    assert res.json["code"] == 422


def test_post_patient_invalid_token_should_raise_401(app, access_token_patient_role):
    """Test post medic with invalid token raises 401 error.

    :param app: flask app instance
    """
    res = app.test_client().post(
        "/patients",
        json={
            "firstName": "Anna",
            "lastName": "Patient",
            "email": "anna.patient@gmail.com",
            "medicIds": [2],
        },
        headers={"Authorization": f"Bearer {access_token_patient_role}123"},
    )

    assert_error_response_structure(res)

    assert res.json["code"] == 401


def test_delete_patient_should_remove_patient_from_db(app, access_token_patient_role):
    """Test delete patient removes patient from db.

    This includes removing the patient from the list of patients of each medic.

    :param app: flask app instance
    """
    patient_id = 5

    # get patient ids associated with medic before deletion
    patient = db.session.get(Patient, patient_id)
    assert patient
    medic_ids = [medic.id for medic in patient.medics]

    res: flask.Response = app.test_client().delete(
        f"/patients/{patient_id}",
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    assert_success_response_structure(res)

    # verify patient was deleted
    assert db.session.get(Patient, patient_id) is None

    # test response contains patient id
    assert res.json["data"] == patient_id

    # test no former medic still has patient in his list of patients
    medics = Medic.query.filter(Medic.id.in_(medic_ids)).all()
    for medic in medics:
        assert patient not in medic.patients


def test_delete_patient_non_existing_should_return_404(
    app, access_token_patient_role
) -> None:
    """Test trying to delete a non existing patient raises 404.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().delete(
        "/patients/1000000",
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_delete_not_authorized_raises_403(app, access_token_medic_role) -> None:
    """Test trying to delete a patient without priviliges raises 403.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().delete(
        "/patients/1000000",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_error_response_structure(res)
    assert res.status_code == 403


def test_get_records_of_patients_should_return_records(
    app, access_token_medic_role
) -> None:
    """Test getting records of a patient returns a list of records.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get(
        "/patients/5/records",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_success_response_structure(res)

    assert len(res.json["data"]) > 0


def test_get_records_of_patients_non_existing_should_raise_404(
    app, access_token_patient_role
) -> None:
    """Test trying to get records of a non-existent patient raises 404.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get(
        "/patients/2/records",
        headers={"Authorization": f"Bearer {access_token_patient_role}"},
    )

    assert_error_response_structure(res)
    assert res.status_code == 404


def test_post_new_record_should_add_record_to_patient(
    app, access_token_medic_role
) -> None:
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
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    # test response boilerplate
    assert_success_response_structure(res, expected_status_code=201)

    # assert the id of the newly created medic is returned
    new_record_id = res.json["data"].get("id")
    assert new_record_id

    # check new medic is in db
    assert db.session.get(Record, new_record_id)


def test_get_record_should_return_record(app, access_token_medic_role) -> None:
    """Test getting a record returns a record.

    :param app: flask app instance
    """
    patient_id = 5
    record_id = 1
    res = app.test_client().get(
        f"/patients/{patient_id}/records/{record_id}",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )
    assert_success_response_structure(res)

    assert len(res.json["data"]) > 0


def test_get_non_existing_record_should_return_404(
    app, access_token_medic_role
) -> None:
    """Test getting a non existing record raises 404.

    :param app: flask app instance
    """
    patient_id = 5
    record_id = 10
    res = app.test_client().get(
        f"/patients/{patient_id}/records/{record_id}",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )
    assert_error_response_structure(res)

    assert res.json["code"] == 404


def test_delete_record_removes_record_from_db(app, access_token_medic_role) -> None:
    """Test deleting a record removes it from the db.

    :param app: flask app instance
    """
    patient_id = 5
    record_id = 1

    # assert record is in db
    assert db.session.get(Record, record_id)
    res = app.test_client().delete(
        f"/patients/{patient_id}/records/{record_id}",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )

    assert_success_response_structure(res)

    # assert recod is no longer in db
    assert db.session.get(Record, record_id) is None

    # test response contains record id
    assert res.json["data"] == record_id


def test_delete_non_existing_record_should_return_404(
    app, access_token_medic_role
) -> None:
    """Test getting a non existing record raises 404.

    :param app: flask app instance
    """
    patient_id = 20
    record_id = 10
    res = app.test_client().delete(
        f"/patients/{patient_id}/records/{record_id}",
        headers={"Authorization": f"Bearer {access_token_medic_role}"},
    )
    assert_error_response_structure(res)

    assert res.json["code"] == 404


def test_delete_record_not_logged_in_raises_401(app) -> None:
    """Test calling delete record without being logged in raises 401.

    :param app: flask app instance
    """
    patient_id = 5
    record_id = 1
    res = app.test_client().delete(
        f"/patients/{patient_id}/records/{record_id}",
    )
    assert_error_response_structure(res)

    assert res.json["code"] == 401
