import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from flask import current_app, redirect, render_template, session, url_for

from medical_app.backend.authentication import bp


@bp.route("/login")
def login():
    return current_app.oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True),
        audience=current_app.config["API_AUDIENCE"],
    )


@bp.route("/callback", methods=["GET", "POST"])
def callback():
    token = current_app.oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("auth.home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@bp.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user", {}).get("access_token"), indent=4),
    )
