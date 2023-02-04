from flask import Blueprint

bp = Blueprint("main", __name__)

# ignore flake8 issues:
# routes appears unused, but is used in flask blueprint (F401)
# import not at top of module, because bp has to be initialized first (E402)
# trunk-ignore(flake8/F401)
# trunk-ignore(flake8/E402)
from medical_app.backend.main import routes
