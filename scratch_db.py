from medical_app.backend import create_app, db
from medical_app.backend.models import User

app = create_app()

with app.app_context():
    user_john = User(username="john")
    db.session.add(user_john)
    db.session.commit()
