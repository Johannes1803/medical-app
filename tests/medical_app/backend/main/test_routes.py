import flask

from medical_app.backend.models import Medical


def assert_success_response_structure(res) -> None:
    assert res.status_code == 200
    assert res.json["status"] == "success"
    assert res.json["data"]


def assert_error_response_structure(res) -> None:
    assert res.status_code >= 300
    assert res.json["status"] == "error"
    assert res.json["message"]
    assert res.json["code"]

    assert res.status_code == res.json["code"]


def test_get_medics_should_return_medics_array(app):
    res: flask.Response = app.test_client().get("/medics")

    assert_success_response_structure(res)

    assert len(res.json["data"]) > 0


def test_post_medic_should_create_new_medic(app):
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


def test_get_medic_should_return_medic(app) -> None:
    # ToDo: Link medic id to test setup
    res: flask.Response = app.test_client().get("/medics/1")

    assert_success_response_structure(res)


def test_get_medic_non_existing_should_return_404(app) -> None:
    res: flask.Response = app.test_client().get("/medics/1000000")

    assert res.status_code == 404

    assert_error_response_structure(res)
