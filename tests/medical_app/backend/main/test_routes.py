import flask


def test_get_medics_should_return_list(app):
    res: flask.Response = app.test_client().get("/medics/1")

    assert res.status_code == 200
    assert res.json["status"] == "success"

    assert res.json["data"]
