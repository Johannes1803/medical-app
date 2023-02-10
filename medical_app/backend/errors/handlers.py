from flask import jsonify
from medical_app.backend.errors import bp


@bp.app_errorhandler(404)
def not_found(error):
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
