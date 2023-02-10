import flask


def test_get_medic_should_return_medic(app):
    # ToDo: Link medic id to test setup
    res: flask.Response = app.test_client().get("/medics/1")

    assert res.status_code == 200

    assert res.json["status"] == "success"
    assert res.json["data"]


def test_get_medic_non_existing_should_return_404(app):
    res: flask.Response = app.test_client().get("/medics/1000000")

    assert res.status_code == 404

    assert res.json["status"] == "error"
    assert res.json.get("message")
    assert res.json["code"] == 404
