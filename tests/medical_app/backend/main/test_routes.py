import flask


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


def test_get_medic_should_return_medic(app) -> None:
    # ToDo: Link medic id to test setup
    res: flask.Response = app.test_client().get("/medics/1")

    assert_success_response_structure(res)


def test_get_medic_non_existing_should_return_404(app) -> None:
    res: flask.Response = app.test_client().get("/medics/1000000")

    assert res.status_code == 404

    assert_error_response_structure(res)
