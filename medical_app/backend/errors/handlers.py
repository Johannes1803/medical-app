# from oauthlib.oauthlib.oauth2.rfc6749.errors import OAuth2Error
from authlib.oauth2.base import OAuth2Error
from flask import jsonify

from medical_app.backend.errors import bp


@bp.app_errorhandler(OAuth2Error)
def not_allowed_app(error: OAuth2Error):
    return (
        jsonify(
            {
                "status": "error",
                "code": error.status_code,
                "message": error.description,
            }
        ),
        error.status_code,
    )


@bp.app_errorhandler(404)
def resource_not_found(error):
    return (
        jsonify(
            {
                "status": "error",
                "code": 404,
                "message": "Resource not found",
            }
        ),
        404,
    )


@bp.errorhandler(404)
def route_invalid(error):
    return (
        jsonify(
            {
                "status": "error",
                "code": 404,
                "message": "Resource not found",
            }
        ),
        404,
    )


@bp.app_errorhandler(422)
def unprocessable_entity(error):
    return (
        jsonify(
            {
                "status": "error",
                "code": 422,
                "message": "Unprocessable Entity",
            }
        ),
        422,
    )


@bp.app_errorhandler(500)
def internal_server_error(error):
    return (
        jsonify(
            {
                "status": "error",
                "code": 500,
                "message": "Internal Server Error",
            }
        ),
        500,
    )
