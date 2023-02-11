import flask

from medical_app.backend.models import Medical


def assert_success_response_structure(res) -> None:
    """Validate success response structure.

    :param res: flask response object
    """
    assert res.status_code == 200
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
    res: flask.Response = app.test_client().get("/medics")

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
    assert_success_response_structure(res)

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

    assert res.status_code == 404

    assert_error_response_structure(res)


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

    # test response contains medic id
    assert res.json["data"] == 1

    # test no former patient still has medic in his list of medics
    # ToDo


def test_delete_medic_non_existing_should_return_404(app) -> None:
    """Test trying to delete a non existing medic raises 404.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().delete("/medics/1000000")

    assert res.status_code == 404

    assert_error_response_structure(res)


def test_get_patients_of_medic(app) -> None:
    """Test get patients of medic returns array of patients.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics/1/patients")

    assert_success_response_structure(res)

    # we know that medic one has a patient
    assert len(res.json["data"]) > 0


def test_get_patients_of_medic_non_existing_should_return_404(app) -> None:
    """Test get medic with non-existing id raises 404 error.

    :param app: flask app instance
    """
    res: flask.Response = app.test_client().get("/medics/1000000/patients")

    assert res.status_code == 404

    assert_error_response_structure(res)
